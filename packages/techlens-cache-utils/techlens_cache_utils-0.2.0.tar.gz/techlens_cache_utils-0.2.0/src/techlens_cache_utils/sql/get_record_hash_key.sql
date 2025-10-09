select * 
    from <table_name> 
    where hash=:hash
    and key=:key
    order by rowid desc
    limit 1
