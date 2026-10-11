# White Bird

**White Bird** is a lightweight Python tool for checking possible public profile URLs across multiple platforms.

## Features

- Simple, color-coded terminal interface
- Supports multiple platform URLs
- Nano-based URL configuration
- Checks public profile pages for a supplied username
- Displays results directly in Termux
- No HTML reports or scan log files
- Python standard library for application logic

## Requirements

- Android with Termux
- Python 3
- Nano editor

## Installation

Clone or download this repository, then open its directory in Termux.
1
```bash
git clone https://codeberg.org/Firewall-Crusher/White-Bird.git
```
```bash
cd White-Bird
```
```bash
chmod +x install.sh
./install.sh
```

## Usage

Start the application:

```bash
python white_bird.py
```

Main menu:

1. SET Scan URL
2. View Reports
0. Exit

Select **Scan URL**, enter your target platform URLs in Nano, save the file, and exit the editor. Then enter the username you want to check.

Enter one URL per line. Lines beginning with `#` are ignored.

## Results

Results are displayed directly in the terminal. `View Reports` displays results from the current running session.

The application stores the configured URL list in `sites.json`. It does not generate HTML or JSON scan reports.

An HTTP 200 response only indicates that a page is accessible. It does not confirm that an account exists or belongs to a particular person.

## Developer

**Firewall-Crusher**

Profile: https://codeberg.org/Firewall-Crusher

## License

See the `LICENSE` file if one is included in this repository.
