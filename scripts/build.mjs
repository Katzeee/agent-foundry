import { createHash } from "node:crypto";
import { execFileSync, spawnSync } from "node:child_process";
import { cp, mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const root = path.resolve(import.meta.dirname, "..");
const distRoot = path.join(root, "dist");

function runValidation() {
  const result = spawnSync(process.execPath, [path.join(root, "scripts", "validate.mjs")], {
    cwd: root,
    stdio: "inherit"
  });
  if (result.status !== 0) process.exit(result.status ?? 1);
}

function git(...args) {
  try {
    return execFileSync("git", args, { cwd: root, encoding: "utf8" }).trim();
  } catch {
    return "unknown";
  }
}

async function writeJson(target, value) {
  await mkdir(path.dirname(target), { recursive: true });
  await writeFile(target, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

async function allFiles(directory) {
  const files = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const target = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await allFiles(target));
    else if (entry.isFile()) files.push(target);
  }
  return files.sort();
}

async function hashes(directory) {
  const result = {};
  for (const file of await allFiles(directory)) {
    const relative = path.relative(directory, file).replaceAll("\\", "/");
    result[relative] = createHash("sha256").update(await readFile(file)).digest("hex");
  }
  return result;
}

runValidation();
const catalog = JSON.parse(await readFile(path.join(root, "catalog.json"), "utf8"));

if (path.dirname(distRoot) !== root || path.basename(distRoot) !== "dist") {
  throw new Error(`Refusing to clean unexpected output path: ${distRoot}`);
}
await rm(distRoot, { recursive: true, force: true });
await mkdir(distRoot, { recursive: true });

for (const [name, config] of Object.entries(catalog.skills)) {
  if (config.publish) {
    await cp(path.join(root, "skills", name), path.join(distRoot, "skills", name), { recursive: true });
  }
}

const marketplacePlugins = [];
for (const plugin of catalog.plugins) {
  const pluginRoot = path.join(distRoot, "plugins", plugin.name);
  for (const skill of plugin.skills) {
    await cp(path.join(root, "skills", skill), path.join(pluginRoot, "skills", skill), { recursive: true });
  }

  await writeJson(path.join(pluginRoot, ".codex-plugin", "plugin.json"), {
    name: plugin.name,
    version: plugin.version,
    description: plugin.description,
    author: { name: catalog.publisher.name },
    repository: catalog.publisher.repository,
    skills: "./skills/",
    interface: {
      displayName: plugin.interface.displayName,
      shortDescription: plugin.interface.shortDescription,
      longDescription: plugin.interface.longDescription,
      developerName: catalog.publisher.name,
      category: plugin.category,
      capabilities: [],
      defaultPrompt: plugin.interface.defaultPrompt
    }
  });

  marketplacePlugins.push({
    name: plugin.name,
    source: {
      source: "local",
      path: `./plugins/${plugin.name}`
    },
    policy: {
      installation: "AVAILABLE",
      authentication: "ON_INSTALL"
    },
    category: plugin.category
  });
}

await writeJson(path.join(distRoot, ".agents", "plugins", "marketplace.json"), {
  name: catalog.marketplace.name,
  interface: { displayName: catalog.marketplace.displayName },
  plugins: marketplacePlugins
});

const publishedSkills = Object.entries(catalog.skills).filter(([, config]) => config.publish).map(([name]) => name);
const releaseReadme = `# ${catalog.marketplace.displayName}\n\nThis branch is generated from the \`source\` branch. Do not edit it directly.\n\n## Published skills\n\n${publishedSkills.map((name) => `- \`${name}\``).join("\n")}\n\n## Published plugins\n\n${catalog.plugins.map((plugin) => `- \`${plugin.name}@${plugin.version}\`: ${plugin.skills.join(", ")}`).join("\n")}\n\nDevelopment sources and build configuration live on the [\`source\` branch](${catalog.publisher.repository}/tree/source).\n`;
await writeFile(path.join(distRoot, "README.md"), releaseReadme, "utf8");

await mkdir(path.join(distRoot, ".github", "workflows"), { recursive: true });
await cp(path.join(root, ".github", "workflows", "publish.yml"), path.join(distRoot, ".github", "workflows", "publish.yml"));

const sourceCommit = process.env.GITHUB_SHA || git("rev-parse", "HEAD");
const sourceDate = process.env.SOURCE_DATE_EPOCH
  ? new Date(Number(process.env.SOURCE_DATE_EPOCH) * 1000).toISOString()
  : git("show", "-s", "--format=%cI", sourceCommit);
const sourceDirty = process.env.CI ? false : git("status", "--porcelain") !== "";
await writeJson(path.join(distRoot, "build-manifest.json"), {
  sourceBranch: "source",
  sourceCommit,
  sourceDate,
  sourceDirty,
  files: await hashes(distRoot)
});

console.log(`Built ${publishedSkills.length} standalone skills and ${catalog.plugins.length} plugins in dist/.`);
