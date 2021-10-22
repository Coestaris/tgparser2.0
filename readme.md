# Telegram Parser v2.0

Basic installation be like:

```shell
sudo apt install python3 # if needed
git clone https://github.com/Coestaris/tgparser2.0
cd tgparser2.0
pip3 install -r requirements.txt
```

Then you need to transform telegram export into more FRIENDLY format using `migrate` subcommand. Example:

```shell
python3 --verbose --sqlite --database parser.db migrate <path-to-telegram-export-directory>
```

Then you can run local server with your statistics. Example
```shell
python3 --verbose --sqlite --database parser.db server
```

Use `--help` or `-h` flags to get more information about available options.