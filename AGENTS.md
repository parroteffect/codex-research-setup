# Distribution repository instructions

This is the **workflow distribution repository**, not the user's research project.
The research project's actual instructions are in `payload/AGENTS.md`.

When asked to install this repository into another project:
1. Read `README.md` and `BOOTSTRAP.md` before making changes.
2. Keep the source checkout separate from the target. Do not install over this repository.
3. The main agent may perform bootstrap setup directly; no engineer must exist yet.
4. Preserve target code, project-specific instructions, research state, model/effort,
   credentials, and security settings. Never run heavy experiments.
5. Review the installer before executing it. Start with its default dry run.
6. Distinguish files installed from a fresh Codex session loading the configuration.

When asked to maintain this distribution:
- Keep all original research/review/implementation guidance except explicitly requested changes.
- Keep main's direct code access, single writer, USER-ONLY final experiments, and adaptive high/xhigh.
- Preserve active research invention and mathematical analysis; distinguish output style,
  implementation scope, and execution limits from research breadth and depth.
- Do not add rigid idea quotas or claim a measured creativity/potential improvement without evidence.
- Preserve standard as the default for new tasks and monk as an explicit, task-scoped choice.
  Keep monk's creative exploration, mathematical research allowance, and deferred prior-art comparison.
- Update payload checksums in `manifest.json` after intentional payload edits.
- Run only `python3 -m unittest discover -s tests -v` or similarly light, reviewed checks.
- Do not start Codex, a model, GPU jobs, package downloads, or workflow installation in the source root.

- v5.3 maintenance: preserve default research plus independent goal/monk overlays, role-specific
  effort dispatch (Engineer high/xhigh; QA medium/high; Supervisor high/important xhigh), and
  create-only user goal settings. The goal guard is bookkeeping, never an experiment runner.
