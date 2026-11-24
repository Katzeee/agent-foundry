<!-- agent-foundry:begin code-design -->
## Code Design

**Refactor, don't patch.** When a new capability outgrows the architecture, reshape it around a better abstraction that unifies existing and new behavior and makes similar additions require fewer changes. Bring every obstructing implementation into scope; a smaller diff is no reason to preserve a weaker design. Reshape or remove existing structures as the design requires. Add no compatibility layers, and notify the human when compatibility concerns arise.
<!-- agent-foundry:end code-design -->
