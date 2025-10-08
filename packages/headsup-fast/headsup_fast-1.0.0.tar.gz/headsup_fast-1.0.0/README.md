# HeadsUp-Fast

A trivial alternative to Ubuntu's landscape-info with no external dependencies, that runs in 10% of the time of `/etc/update-motd.d/50-landscape-sysinfo`. Because perf matters.

Originally forked from [landscape-sysinfo-mini](https://github.com/jnweiger/landscape-sysinfo-mini/). Changes include removing utmp dependency and generally speeding things up.

## Features

- **Fast**: Runs in ~10% of the time of the standard Ubuntu landscape-sysinfo
- **Zero dependencies**: Pure Python 3.6+ with standard library only
- **Linux-focused**: Designed specifically for Linux systems with `/proc` filesystem
- **Drop-in replacement**: Easy to replace Ubuntu's default MOTD script

## Sample Output

```
  System information as of Wed Sep 18 15:04:32 2025

  System load:  12.5%              Processes:        145
  Usage of /:   67.2% of 29.84GB   Users logged in:  2
  Memory usage: 41.3%              IP address for eth0: 192.168.1.100
  Swap usage:   2.1%
```

## Installation

### Option 1: Install as a command

```bash
pip install headsup-fast
```

Then run:
```bash
headsup
```

### Option 2: Replace Ubuntu's default MOTD (recommended)

1. Copy the script to your motd directory:
   ```bash
   sudo cp headsup.py /etc/update-motd.d/50-headsup
   sudo chmod +x /etc/update-motd.d/50-headsup
   ```

2. Remove the standard Ubuntu one (optional):
   ```bash
   sudo rm /etc/update-motd.d/50-landscape-sysinfo
   ```

3. Test it:
   ```bash
   sudo run-parts /etc/update-motd.d/
   ```

## Requirements

- Linux system with `/proc` filesystem
- Python 3.6 or higher
- Standard Linux utilities: `ip`, `who`

## Performance

This implementation focuses on speed by:
- Using `/proc` filesystem directly instead of external tools where possible
- Avoiding heavy dependencies like `python-utmp`
- Efficient parsing and minimal subprocess calls
- Optimized string formatting

## License

MIT License

## Contributing

Bug reports and pull requests are welcome on GitHub.
