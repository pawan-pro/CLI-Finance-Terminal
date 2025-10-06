## Fast Update Directive for Agents

- If chart files are missing, first verify symbol mappings used for MT5 data fetching.
- Before chart generation, cross-check symbol codes against broker listings and add debugging to print the actual queried symbols and any symbol suffixes (`.sd`, `.USD`, etc).
- Agents should add a step:
    - At data fetch: Log (1) symbol attempted, (2) available symbols in MT5, (3) found/not found.
    - At chart generation: Log input series for chart.
- If symbols are mismatched, implement a correction routine:
    - Try with `.sd` or other expected suffixes and retry data fetch.
    - Log all retry attempts and discovered working symbol names.
- If still no data, escalate to prompt-updates.md with list of failing symbols and error prints.
- Update the symbol mapping dictionary and fetching calls in code to use the correct suffixes.

---

- If chart embedding continues to fail due to missing files, integrate direct warnings inside report PDF indicating missing charts for specific symbols, along with suspected symbol errors for user awareness.


please keep a track of changes in tasks in prompt-updates.md wrt ongoing and completed tasks. 