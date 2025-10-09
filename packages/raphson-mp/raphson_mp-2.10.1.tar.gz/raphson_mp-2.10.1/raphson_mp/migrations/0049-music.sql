-- Due to a bug, some millisecond timestamps may have ended up in the history table
DELETE FROM history WHERE timestamp > 1000000000000;
