select * 
    from <table_name> 
    where hash=:hash
    order by rowid desc
    limit 1
