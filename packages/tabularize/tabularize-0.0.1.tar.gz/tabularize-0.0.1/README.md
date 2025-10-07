<!--suppress HtmlDeprecatedAttribute-->
<div align="center">
   <h1>🗂️ Tabularize</h1>
</div>

<hr />

<div align="center">

[💼 Purpose](#purpose)

</div>

<hr />

# Purpose

Tabularize aids in the parsing of semi-structured data in a table-like format into Python dictionaries given no
knowledge of the expected data format.

While packages such as [csv](https://docs.python.org/3/library/csv.html), [pandas](https://pypi.org/project/pandas/),
and [TextFSM](https://pypi.org/project/textfsm/) exist, they require the input data to be in a more structured form. For 
example, requiring clearly distinguishable delimiters, fixed column widths, or knowledge about the data to deduce the 
start and end of a column based on data types. Tabularize is designed for instances where there can be guess-work due to 
input data not following these constraints.

This package's design takes influence from the [Name/Finger protocol](https://datatracker.ietf.org/doc/html/rfc742) due
to its non-standardized, human-readable status reports that tend to give machines a harder time.

Tabularize is _probably not the solution for you_ - that is, modern protocols are often machine-readable, or they offer 
a means to make it easily machine-readable. It shines when you need to parse semi-structured, tabular data where the
schema is unknown (a situation you should avoid) or when you need tabular data parsed quickly.

# Usage

Tabularize is offered as both an API for developers and a command-line tool. To install it:

```shell
python3 -m pip install tabularize
```

### Command-Line Usage

The `tabularize` command is available upon installation. The command takes as a parameter a list of files, where it will 
locate the first non-blank line of each one to determine headers then print out a JSON object for each later, parsed 
entry. For example:

```shell
tabularize path-to-file path-to-another-file
```

Sometimes, automatic header detection may not function as expected when there is a degree of ambiguity since Tabularize
only analyzes the singular header line, not the content, to derive column names. For example, given the following data:

```terminaloutput
    Line      User       Host(s)              Idle Location
   1 vty 0               idle                 00:00:05 192.168.1.1
*  2 vty 1               idle                 00:00:00 192.168.1.2
```

By default, Tabularize will misinterpret the headers and assume that a `Idle Location` header exists rather than two
separate `Idle` and `Location` headers. Since Tabularize works sequentially, you can specify an `Idle` header, and it
will resolve the error without having to specify a `Location` header:

```shell
tabularize -H Idle path-to-finger-output
```

The `tabularize` command also supports piping. When piping is desired, use the file name `-`:
```shell
cat file-to-parse | tabularize -
```

Tabularize operates at the byte level; however, it prints out data as JSON, which does not support bytes. As a result,
it decodes the data before printing it to the terminal. You can customize the encoding and error resolution strategy
using the `--encoding` and `--errors` options:

```shell
tabularize --encoding utf-8 --errors backslashreplace path-to-file
```

### API Usage

Programs integrating Tabularize will need to independently determine the appropriate line to extract headers from 
alongside body lines. The headers are then reused for body line parsing. For example:

```python
import tabularize


data = b"""
Name    Ice Cream Preference
James   Mint Chocolate Chip
""".splitlines()

headers = tabularize.parse_headers(
        data[0]
    )

for line in data[1:]:
    print(tabularize.parse_body(headers, line))
```

# Samples

Tabularize is particularly useful for parsing the Name/Finger Protocol given that the `fingerd` server implementation is 
unknown due to its lack of standardization. However, if the server implementation is known, consider using a 
regular expression-based solution instead such as [TextFSM](https://pypi.org/project/textfsm/) as the data types can
help indicate the start and end of output.

<details style="border: 1px solid; border-radius: 8px; padding: 8px; margin-top: 4px;">
<summary>🐧 Debian fingerd</summary>

```terminaloutput
Login     Name       Tty      Idle  Login Time   Office     Office Phone
alfred              *pts/0      1d  Oct 06 19:56 (192.168.1.1)
bert                 pts/1      2d  Oct 06 12:34 (:pts/0:S.0)
chase                pts/2      3d  Oct 06 05:43 (:pts/0:S.1)
```

```json
[
  {"Login": "alfred", "Tty": "*pts/0", "Idle": "1d", "Login Time": "Oct 06 19:56", "Office": "(192.168.1.1)"},
  {"Login": "bert", "Tty": "pts/1", "Idle": "2d", "Login Time": "Oct 06 12:34", "Office": "(:pts/0:S.0)"},
  {"Login": "chase", "Tty": "pts/2", "Idle": "3d", "Login Time": "Oct 06 05:43", "Office": "(:pts/0:S.1)"}
]
```

</details>

<details style="border: 1px solid; border-radius: 8px; padding: 8px; margin-top: 4px;">
<summary>📡 Cisco fingerd</summary>

```terminaloutput
    Line       User       Host(s)              Idle       Location
   1 vty 0                idle                 00:00:00 
```

```json
[
  {"Line": "1 vty 0", "Host(s)": "idle", "Idle": "00:00:00"}
]
```

</details>