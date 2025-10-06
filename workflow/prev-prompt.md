# Additional Agent Debugging Instructions

- During MT5 data fetch for **charts**, log and check the exact symbol used, and list the broker’s available symbols. If the expected symbol (e.g., `US500Roll`) does not exist, try:  
    - Adding `.sd` or other expected broker-specific suffix.
    - Log all attempts and results.

- If fetch fails for a symbol, retry with alternate (known) suffixes. If still fails, print/log all failed combinations and escalate to prompt-updates.md.

- At every stage (fetch, chart generation, embedding), include the exact error message, symbol attempted, and suspected root cause.  
- If available, update code or symbol dictionary to use correct broker symbol format for **MT5**.

---
