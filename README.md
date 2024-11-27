# gmail
```
usage: gmail [-h] [-H] [-v] [-V] [--config FILE] [--print-config]
             [--print-url] [--completion [SHELL]]
             COMMAND ...

Google `mail` command line interface.

Specify one of:
  COMMAND
    download            Download mail messages.
    labels              List labels.
    list                List mail messages.

General options:
  -h, --help            Show this help message and exit.
  -H, --long-help       Show help for all commands and exit.
  -v, --verbose         `-v` for detailed output and `-vv` for more detailed.
  -V, --version         Print version number and exit.
  --config FILE         Use config `FILE` (default: `~/.pygoogle.toml`).
  --print-config        Print effective config and exit.
  --print-url           Print project url and exit.
  --completion [SHELL]  Print completion scripts for `SHELL` and exit
                        (default: `bash`).

See `gmail COMMAND --help` for help on a specific command.
```

## gmail download
```
usage: gmail download [-h] MSG_ID

The `gmail download` program downloads a mail message.

positional arguments:
  MSG_ID      The id of the message to download.

options:
  -h, --help  Show this help message and exit.
```

## gmail labels
```
usage: gmail labels [-h] [--show-counts] [--limit LIMIT] [--pretty-print]

The `gmail labels` program lists labels.

options:
  -h, --help      Show this help message and exit.
  --show-counts   Show message counts.
  --limit LIMIT   Limit execution to `LIMIT` number of items.
  --pretty-print  Pretty-print items.
```

## gmail list
```
usage: gmail list [-h] [--print-message | --print-listing | --pretty-print]
                  [--msg-id MSG_ID] [--label-ids [LABEL_IDS ...]]
                  [--has-attachments] [--has-images] [--has-videos]
                  [--search-query SEARCH_QUERY] [--limit LIMIT]

The `gmail list` program lists mail messages.

options:
  -h, --help            Show this help message and exit.
  --limit LIMIT         Limit execution to `LIMIT` number of items.

Printing options:
  These options are mutually exclusive.

  --print-message, --print-msg
                        Print message.
  --print-listing       Print listing.
  --pretty-print        Pretty-print items.

Filtering options:
  --msg-id, --msgid MSG_ID
                        Operate on `MSG_ID` only.
  --label-ids [LABEL_IDS ...]
                        Match labels (default: `['INBOX']`).
  --has-attachments     Search messages with any files attached.
  --has-images          Search messages with image files attached.
  --has-videos          Search messages with video files attached.
  --search-query SEARCH_QUERY
                        Gmail search box query pattern.
```

