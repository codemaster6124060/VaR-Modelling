Class notes
<pre>
    Portfolio or book class for keeping track of trades
        How to handle Capital?  Create dummy asset worth $1?
    Input class
        To handle all inputs including reading YAML files
        This is for static inputs.
        How do we handle dynamic inputs, prices each day?
        dollars per point.  From the paper, this was contract size (volume) since we are using ETFs, should this be $1
    Core calc class
        N, TR, PDC, (20, 10, 55) day moving averages, DollarVolatiliy, H, L PDN.
        PDC, PDN, moving averages need to be saved and reload for the previous day each day.  Do we build a class to hold this in memory or disk?
    Reporting
        How do we handle this?
</pre>
  <br/><br/>
    Backtesting TBD.
    
    
    