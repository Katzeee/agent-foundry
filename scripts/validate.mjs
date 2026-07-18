import { createHash } from "node:crypto";
import { readdir, readFile, stat } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const root = path.resolve(import.meta.dirname, "..");
const catalogPath = path.join(root, "catalog.json");
const distRoot = path.join(root, "dist");
const slugPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const semverPattern = /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/;

function fail(message) {
  throw new Error(message);
}

async function exists(target) {
  try {
    await stat(target);
    return true;
  } catch (error) {
    if (error.code === "ENOENT") return false;
    throw error;
  }
}

async function json(target) {
  return JSON.parse(await readFile(target, "utf8"));
}

function frontmatter(markdown, source) {
  const match = markdown.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
  if (!match) fail(`${source} has no YAML frontmatter`);
  const fields = new Map();
  for (const line of match[1].split(/\r?\n/)) {
    const field = line.match(/^([a-zA-Z0-9_-]+):\s*(.*?)\s*$/);
    if (field) fields.set(field[1], field[2]);
  }
  return fields;
}

async function validateLinks(markdown, skillDirectory, source) {
  const prose = markdown.replace(/^(```|~~~).*?^\1\s*$/gms, "");
  for (const match of prose.matchAll(/\[[^\]]*\]\(([^)]+)\)/g)) {
    const raw = match[1].trim().split(/\s+/)[0].replace(/^<|>$/g, "");
    if (!raw || raw.startsWith("#") || /^[a-z][a-z0-9+.-]*:/i.test(raw)) continue;
    const relative = decodeURIComponent(raw.split("#", 1)[0]);
    if (!(await exists(path.resolve(skillDirectory, relative)))) {
      fail(`${source} links to missing file: ${raw}`);
    }
  }
}

async function validateSource(catalog) {
  if (!slugPattern.test(catalog.marketplace?.name ?? "")) fail("marketplace.name must be kebab-case");
  if (!catalog.marketplace?.displayName) fail("marketplace.displayName is required");
  if (!catalog.publisher?.name) fail("publisher.name is required");
  if (!/^https:\/\//.test(catalog.publisher?.repository ?? "")) fail("publisher.repository must be an https URL");
  if (!catalog.skills || Array.isArray(catalog.skills)) fail("skills must be an object");
  if (!Array.isArray(catalog.plugins)) fail("plugins must be an array");

  const sourceDirectories = (await readdir(path.join(root, "skills"), { withFileTypes: true }))
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
  const declaredSkills = Object.keys(catalog.skills).sort();
  if (JSON.stringify(sourceDirectories) !== JSON.stringify(declaredSkills)) {
    fail(`catalog skills do not match skills/: declared [${declaredSkills}], found [${sourceDirectories}]`);
  }

  for (const [name, config] of Object.entries(catalog.skills)) {
    if (!slugPattern.test(name)) fail(`invalid skill name: ${name}`);
    if (typeof config.publish !== "boolean") fail(`skills.${name}.publish must be boolean`);
    const directory = path.join(root, "skills", name);
    const skillPath = path.join(directory, "SKILL.md");
    const markdown = await readFile(skillPath, "utf8");
    const fields = frontmatter(markdown, `skills/${name}/SKILL.md`);
    if (fields.get("name") !== name) fail(`skills/${name}/SKILL.md name must equal its directory name`);
    if (!fields.get("description")) fail(`skills/${name}/SKILL.md needs a description`);
    await validateLinks(markdown, directory, `skills/${name}/SKILL.md`);
  }

  const pluginNames = new Set();
  for (const plugin of catalog.plugins) {
    if (!slugPattern.test(plugin.name ?? "")) fail(`invalid plugin name: ${plugin.name}`);
    if (pluginNames.has(plugin.name)) fail(`duplicate plugin: ${plugin.name}`);
    pluginNames.add(plugin.name);
    if (!semverPattern.test(plugin.version ?? "")) fail(`${plugin.name} has an invalid version`);
    if (!plugin.description) fail(`${plugin.name} needs a description`);
    if (!Array.isArray(plugin.skills) || plugin.skills.length === 0) fail(`${plugin.name} must include at least one skill`);
    if (new Set(plugin.skills).size !== plugin.skills.length) fail(`${plugin.name} contains duplicate skills`);
    for (const skill of plugin.skills) {
      if (!(skill in catalog.skills)) fail(`${plugin.name} references undeclared skill: ${skill}`);
    }
    for (const key of ["displayName", "shortDescription", "longDescription", "defaultPrompt"]) {
      if (!plugin.interface?.[key]) fail(`${plugin.name}.interface.${key} is required`);
    }
  }
}

async function sha256(target) {
  return createHash("sha256").update(await readFile(target)).digest("hex");
}

async function filesBelow(directory) {
  const result = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const target = path.join(directory, entry.name);
    if (entry.isDirectory()) result.push(...await filesBelow(target));
    else if (entry.isFile()) result.push(target);
  }
  return result.sort();
}

async function assertSameTree(left, right, label) {
  const leftFiles = (await filesBelow(left)).map((file) => path.relative(left, file).replaceAll("\\", "/"));
  const rightFiles = (await filesBelow(right)).map((file) => path.relative(right, file).replaceAll("\\", "/"));
  if (JSON.stringify(leftFiles) !== JSON.stringify(rightFiles)) fail(`${label} has a different file set`);
  for (const relative of leftFiles) {
    if (await sha256(path.join(left, relative)) !== await sha256(path.join(right, relative))) {
      fail(`${label} differs at ${relative}`);
    }
  }
}

async function validateDist(catalog) {
  if (!(await exists(distRoot))) fail("dist/ does not exist; run npm run build first");
  const marketplace = await json(path.join(distRoot, ".agents", "plugins", "marketplace.json"));
  if (marketplace.name !== catalog.marketplace.name) fail("generated marketplace name is stale");
  if (marketplace.plugins.length !== catalog.plugins.length) fail("generated marketplace plugin count is stale");

  for (const [name, config] of Object.entries(catalog.skills)) {
    if (config.publish) {
      await assertSameTree(path.join(root, "skills", name), path.join(distRoot, "skills", name), `published skill ${name}`);
    } else if (await exists(path.join(distRoot, "skills", name))) {
      fail(`non-published skill ${name} exists in dist/skills`);
    }
  }

  for (const plugin of catalog.plugins) {
    const pluginRoot = path.join(distRoot, "plugins", plugin.name);
    const manifest = await json(path.join(pluginRoot, ".codex-plugin", "plugin.json"));
    if (manifest.name !== plugin.name || manifest.version !== plugin.version) fail(`${plugin.name} manifest is stale`);
    for (const skill of plugin.skills) {
      await assertSameTree(path.join(root, "skills", skill), path.join(pluginRoot, "skills", skill), `${plugin.name}/${skill}`);
    }
  }
}

try {
  const catalog = await json(catalogPath);
  await validateSource(catalog);
  if (process.argv.includes("--dist")) await validateDist(catalog);
  console.log(process.argv.includes("--dist") ? "Source and distribution are valid." : "Source catalog and skills are valid.");
} catch (error) {
  console.error(`Validation failed: ${error.message}`);
  process.exitCode = 1;
}
