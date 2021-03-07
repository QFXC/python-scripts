---------
FIX Logs:
---------

-   FIX(Financial Information eXchange) See:
    http://www.fixtradingcommunity.org/pg/structure/about/overview
-   Sample FIX logs are available in fix_logs/FIX*.log

1.  Write a python script that processes the FIX log files and reports a
    summary of the number of orders broken down by order status (Tag 39) in
    categories filled (39=2), partially filled (39=1), and canceled (39=4)

2.  Write a python script that processes the FIX log files and reports a
    summary of the quantity filled on instrument (Tag 55) ES.  Use Execution
    reports (Tag 35=8) and examine the CumQty field (Tag 14).  Note that an 
    order (uniquely identified by ClOrdID, Tag 11) can receive multiple
    execution reports and that the CumQty represents the Cumulative Quantity
    so intermediate quantities should not be counted multiple times.
