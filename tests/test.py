import pathlib
import sys
sys.path.append("/home/lin/projecs/yam-parse-py")

from parser.yam_parser import parse


parse(f"{pathlib.Path(__file__).parent.resolve()}/example.yam")
