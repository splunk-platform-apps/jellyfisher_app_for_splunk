# Source Directory (src) - UCC Framework Build Assets

This directory contains the assets and configuration files required by the [Splunk Universal Configuration Console (UCC) framework](https://splunk.github.io/addonfactory-ucc-generator/).


While the core logic and custom code for this add-on are developed and maintained independently in the [`jellyfisher`](../jellyfisher/) directory, this `src` directory serves a specific build purpose: packaging and compiling the required `jellyfish` OS-dependent Python library.

Because `jellyfish` includes Rust implementations that must be compiled for specific operating systems (Linux, Windows, macOS) to run properly within a Splunk environment, we leverage the UCC framework to handle the cross-platform dependency resolution and packaging.

## Layout

```
.
├── jellyfisher/            # add-on source code. All active development of the add-on logic happens here.
├── src/                    # UCC Framework assets needed for the build process
│   ├── lib/                # libraries needed (incl. Jellyfish)
│   │   └── requirements.txt
│   └── app.manifest
└── globalConfig.json       # Spec for the UCC Framework
```

## Bundle the Add-on Locally

### Prerequisites

- Python 3.9+
- Install required dependencies

```bash
# Navigate to the root directory of the repository
~ pip install requirements.txt
```

### How to Build

To package the OS-dependent libraries and opportunely bundle the app execute:

```bash
# Navigate to the root directory of the repository
~ make package
```

The resulting archived add-on can be found at `build/jellyfisher.tgz`.

## ⚠️ Important Notes

- Do not place core add-on code in this `src/` directory. This directory should remain **restricted to UCC build assets**. Any custom Python scripts, inputs, or Splunk configurations should remain in `jellyfisher/` instead.

- OS-Dependent Libraries: if additional OS-dependent libraries are needed in the future,
  - add them to the `lib/requirements.txt` file in this `src/` directory
  - add their opportune specifications in the `globalConfig.json` file used by the UCC framework to build alongside the current ones.