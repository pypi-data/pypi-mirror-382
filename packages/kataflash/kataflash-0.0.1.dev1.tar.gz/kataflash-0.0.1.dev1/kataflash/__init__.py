import argparse

def main(args=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.set_defaults(action=cmd_default)

    sp = ap.add_subparsers()
    sp_version = sp.add_parser('version')
    sp_version.set_defaults(action=cmd_version)
    
    args = ap.parse_args(args=args)
    raise SystemExit(args.action(args))
    

def cmd_default(args):
    print(\
            "Welcome to kataflash, a friendly interface for katapult-based flashing!\n"
            "  Homepage: https://github.com/laikulo/kataflash\n"
            "  Kataflash is distrubted under the GNU GPL 3.0, and is bundled with code from the following projects:\n"
            "    - Katapult flashtool (https://github.com/Arksine/katapult)\n"
            "      Katapult includes:\n"
            "      - parts of Klipper (https://github.com/klipper3d/klipper)\n"
            "      - fasthash6 for python (https://github.com/ztanml/fast-hash)\n"
            "run 'kataflash -h' for infromation about using kataflash\n"
            "to use the vendored flashtool directly, run 'kataflashtool' with your usual flashtool args"
          )


def cmd_version(args):
    print(f"This is Kataflash v0.0.0\n  Includes katapult {_get_katapult_version()}")

def _get_katapult_version():
    try:
        from .upstream.info import KATAPULT_REF
    except Exception as e:
        print(e)
        return "<missing>"
    else:
        return KATAPULT_REF
