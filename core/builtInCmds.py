#
# Hi BAKA!
# Comet 1 source code
# Infinite Inc.
# Copyright (c) 2025 Infinite Inc.
# Written by Thiruvalluvan, Prithviraj Kamaraj
# Licenced under the Apache-2.0 Licence
#
# Filename: src\\core\\builtInCmds.py
# Description: Defines built-in commands
#

import os
import sys
import ctypes     as ct
import datetime   as dt
import importlib  as il
import pathlib    as pl
import msvcrt     as ms
import subprocess as sp
import timeit     as ti
import typing     as ty
import zlib       as zl
import commons    as comm
if ty.TYPE_CHECKING:
    import comet


class HelpTxts:
    def __init__(self) -> None:
        # I'm sorry.
        self.helpABOUT       = (
            b"x\x9cs\xc9,.\xc8I\xac,V\xc8\xccK\xcb/\xcaM,\xc9\xcc\xcfSHL\xca/-"
            b"Qp\xce\xcfM-\xd1\xe3\xe2\n\rvtw\xb5\x82\nF\xebf\xc4rq\xf9\x07\x84"
            b"x\xfa\xfb\x05s\xe9f(\xe8+\xe8\xeaf\xa4\xe6\x14p)\x00\x81\x07\x90"
            b"\xa1\x90\x9bZ\\\x9c\x98\x9e\n\x00XO\x1ce"
        )
        self.helpBIN         = (
            b"x\x9c=\x8d1\x0b\xc20\x14\x84\xf7\xf7+\x8eNu\x88\xee\xdd\x84\x8a"
            b"\xb8\xd8Bu\x12\x87g\xfb0\x81$\r}\x19\xf4\xdf\x9b*x\xd3\xf1\x1d"
            b"\xc7\xd7:M\x9e\xdf\x8al\x05\xf2\xca\xb2D\xf6\x18\xe7\x108N\x8a"
            b"\xfa\xdf\xfc<r\x96\t.\xa2z\xb8XmP\xf0\xfar\x0b\x12g\xab[\xa2\xeb"
            b"\xb0?\x1e\x1a\x94\x197c\xefD]\x7f9u\xe7\x81\x8c\xc5\x0e\xc6X\xf1"
            b"\x89P\xd2\xfe\xac_\xe9\n\x11D\x95\x9f\xf2\x01}s.Y"
        )
        self.helpCD          = (
            b"x\x9cu\x8f1o\xc20\x10\x85\xf7\xfb\x15o\xae\x94\xb2\xb3T\x08\x10"
            b"th\x88\x12\xd2\x852D\xc95\xb6\xda\xfa\xa2\xb3\x01\xf5\xdf\xd7\xb6"
            b"\x14\x89\xa1\xdctz\xf7\xbeO\xf6\xdatnd\x8f`\x18\xfdE\x95]\xc0M"
            b"\xf4\xcb\xba\x11\x83U\xee\x83\xe8\xef3Q\xdb\xacv\xdb%\xfa\x01\xa7"
            b"\xc2\x9cq\x9a\xba`\xceD\xabz\xd7\xbem\xcbcC\xa58&\xc4\xa9\xd4\xba"
            b"\xe0\x1f\xcb(\xa1\xb9\xb9\x99#\x04A\x9f\x1f\x12\xb7|zB\x81\xd6"
            b"\xb3\xdea)~\x89q\xa5|\xb5r\xf1\xff\x98\xb3\xb4~_\xa6\xdaz\xf6az"
            b"\x08@\x1c\x06\xb5WNT\xa6? \x8aE\xc4k\x91pW\xfc\x8c\xf1\xfc\xa3L"
            b"\x10\x1d\xaa\xe3\xeb\xa1l\xa80\t(\x0c\x7fOY\xb1\x8f\x0b~\xd8\xfb"
            b"n\xe4?\xf3\xc8q\xa9"
        )
        self.helpCLEAR       = (
            b"x\x9cs\xceIM,*V(\xc9HU\xc8/-)(-Q(N.JM\xcd\xd3\xe3\xe2\n\rvtw\xb5"
            b"RH\x06\xa9P\x88\xd6\xcd\x88\xe5\xe2\xf2\x0f\x08\xf1\xf4\xf7\x0b"
            b"\xe6\xd2\xcdP\xd0W\xd0\xd5\xcdH\xcd)\xe0R\x00\x02\x0f C!7\xb5\xb8"
            b"81=\x15\x00<\x99\x19\x1b"
        )
        self.helpCOMET       = (
            b"x\x9c\x95SMo\xdb0\x0c\xbd\xebW\x10\xb94\xc1\xe6\xee\xbe[\xeah"
            b"\x8d\xb1.\t\xe2\xecP,3 \xdbt,D\x96<}\xd4\xcb~\xfdh\xa5[?\x90\x1e"
            b"j\x18\xb2\xc5\xf7H>\x92\xd2B\xba^\x89\x93\x03\xa9\x1bc;\xe1\xa5"
            b"\xd1@\xafo\x11R\xd3\xa1'\xc0\xa3\xed-\xd2z\xcd\xd8\xf7|~\xcb?C"
            b"\x15\xa1\x1fI\xfb\x93\xb1\xf5f\x97\xadW9KZ\xf8\x04I\xd2\xa2\xea"
            b"\x19\xd0\xb3\xa4\x1f\xe8\xd09q@\xc6\xf2\rO\xb3\xf9\x1d|\xe5\xf79"
            b"\xcb\x1a8\x99`\x81bvR\x0b\x05\n\xbd\x8b9E\xdf+Y\x9dex\x03\xad"
            b"\xd0\xb5\xc2\x11q\x08G<\xb9\x8f\xa3#TBCp\xd1\xde\x01\xe9\x8e\xae"
            b"\x8dQ\xca\x0cR\x1f\xaeY! \x81o\xe6!2\xa0\n\xd6\x8d\x1c\x13w%\x1e"
            b"\xa4\xd6D\x03\xd3D\x83\x92\x1aYQ^\xf0(Eu\xa4f\xd0\xbe\x15VT\xa4"
            b"\x96\x15\x15\xf1\xb2\xb1%6\xf4>\x92\x9f5\x88\x155\xc1\xfc\xb7\xbc"
            b"\x80\xe0\xdb\x92P\xd7/\xc54\x17\xb8T\xe6 l\xfdZ\xcfqLh\x85\x8b<"
            b"\x8bz\x1cX\x1f|\x0c\x04\x8d5\xdd\xff\\R)\xe0\xeb;V(r\x99\xa4\n"
            b"\x85\x9d\xc4\x04\xae\xb2\x88\x1a\xa6\xf4\xa5\x16\x9e\xe7P\x86\xa6"
            b"A;c\x85\xa6\xa1\xd6f\xd0 \xac5\x03y\xe6\x91u\xb6\x8d\xccV:o\xec"
            b"\x89\x15=1C\xff\x9aG\x96\x17,K\xd0\x16\x1f\xd0\x92b\x998\x12Q\xb5"
            b"O\xa8#\xf4\xcbc\xa1\xffPVx\xb2\xee\xac\xd0\xae7\xeeY\xf1\x8e\x15"
            b"\xe1]\xd5\xbf\x18\xfd\xb9\xd3\xc3\xbb\x02(\xe1<\x0c\x86\xc4\x95&"
            b"\xe8Z\x8c\x92O\xb1\xa0J\x8c=A:\xc7X?\x86\xfe\x03\x1f\x80f\x1f\xac"
            b"~\xebL0\x9e\xa7\xf3\r\x87t9\xdf\xce\xd3\x1d\xdf\xe6\xb0\xe5\xe9"
            b"\xfav\x95\xe5|\x017\xf7\xb0[r\xc8V\x04l\xb6\x9cV\xb6\xdfS\xa8\x1b"
            b":\x95\x8e\x94\xb40\xdd\xcf\xd8~\x8c\xbe\xc2!\xe6\xdc_\x8d\x8d\xa7"
            b"\x02\xe9\xce\xfc\n\xc6#L\xaf\x882!\xeb\xc2\x84\xf2\xc9:\x99\xfd"
            b"\x05\xf4\xe1W;"
        )
        self.helpCMD         = (
            b"x\x9cE\xcd;\x0e\x83@\x0c\x04\xd0\xde\xa7\x98\x8e\n\x0e\x90.\x05"
            b"\xa2I\x88\xc4\xe7\x00\x0b8\xc1\xd2\xb2\x8bXo\xc2\xf1C\xc8\xcf\xdd"
            b"\x8c4\xcfUtP^&q\xc6\xa2\xf7\xd3d\xdc\x102\xa2\xb6>\x16\xf9\xe1"
            b"\xdb\xc0:\xa2cU\xb4\xe7\xbclj\xda\x12\xb6;\x89c\xa8G\xc7\xe0\x95"
            b"\xfb\xa8<@\xfe\x1cQyirJG\xbc\x844\x1d\xd9\xce\xf0\xb3\x8aw\x01fa"
            b"Dg\xeeF\xac\xe9,\xe3\xea\x17\xe8(\xe1\xf7q\x88\xbb\xbd\xc5\xd9Jo"
            b"\xde\xab\x87\xe8\x88\xd9,A\xdc-\xa360\x92]\xfd\x8c\x92\x9d\x11\r"
            b"\xd8[\xe5U\xb3'\xd7\xe8L{"
        )
        self.helpDATE        = (
            b"x\x9cs\xc9,.\xc8I\xac,V(\xc9HUH.-*J\xcd+Q(\xae,.I\xcdUHI,I\xd5"
            b"\xe3\xe2\n\rvtw\xb5\x02\xf3\x14\xa2u3b\xb9\xb8\xfc\x03B<\xfd\xfd"
            b"\x82\xb9t3\x14\xf4\x15tu3Rs\n\xb8\x14\x80\xc0\x03\xc8P\xc8M-.NLO"
            b"\x05\x00+\xaf\x1b\xd6"
        )
        self.helpCREDITS     = (
            b"x\x9cs\xc9,.\xc8I\xac,VH.JM\xc9,)\xd6\xe3\xe2\n\rvtw\xb5\x82\t("
            b"D\xebf\xc4rq\xf9\x07\x84x\xfa\xfb\x05s\xe9f(\xe8+\xe8\xeaf\xa4"
            b"\xe6\x14p)\x00\x81\x07\x90\xa1\x90\x9bZ\\\x9c\x98\x9e\n\x00\x9a'"
            b"\x17-"
        )
        self.helpEXIT        = (
            b"x\x9cs\xad\xc8,)V(\xc9HU((\xcaO/J\xcc\xd5\xe3\xe2\n\rvtw\xb5RH"
            b"\x05J)D\xebf\xc4rq\xf9\x07\x84x\xfa\xfb\x05s\xe9f(\xe8+\xe8\xea"
            b"f\xa4\xe6\x14p)\x00\x81\x07\x90\xa1\x90\x9bZ\\\x9c\x98\x9e\n\x00"
            b"U\x15\x16("
        )
        self.helpGET         = (
            b"x\x9c-\x8b\xb1\x0e\x820\x18\x84\xf7\xff)ns\xaa\xeen\x0c\xa4:\x08"
            b"\xc6\x82\x0ba(x\x01\x92\x8a\xa4\xad>\xbf\x7f\x8c7\\\xee\x92\xef"
            b"\xb3\xcc\t~\xc5\xb2f\xc6-R\x1b\x1f\x1f\x17?\x04\xee\x92\xce\xf0"
            b"\xe6^\xa4u\x85-\x8f\x98\x98\xd1\x99\xb9G\xa7L/R\xdcl{)\xab\xc6"
            b"\x89~\x81\xe6\xfew\x91_\x18\x08?\x8eL\x89\x0f\x91\xfa\xda\x9c\xeb"
            b"\xca\x89\x99q\x8013\xc3\xf6\x13N:\xf0T\xc8O\xfc\x02\xa8\n+\xee"
        )
        self.helpHELP        = (
            b"x\x9cs\xc9,.\xc8I\xac,V(\xc9HU\xc8H\xcd)P\xc8M\xcd+\xd5\xe3\xe2"
            b"\n\rvtw\xb5\x82\x08E\xebf\xc4*D\'\xe7\xe7\xe6&\xe6\xa5(\xe8\xe9"
            b"\xe9\xc5rq9\x06\xb9\x87\xfa\xba\xfa\x85\x04sA\xc5\xb9\x14\x80\xc0"
            b"\x19\xaa\xa6$_!\x05b2\xc4\x84\x92\xd4\x8a\x12\x85\xb4\xfc\"..\xff"
            b"\x80\x10O\x7f\xbf`.\xdd\x0c\x05}\x05]]\x90,X\xa7\x07\xc4\xee\xe2"
            b"\xe2\xc4\xf4T\x00\xd3h.d"
        )
        self.helpINTRO       = (
            b"x\x9cs\xc9,.\xc8I\xac,V(\xc9HU(.I,*)-\x00\xd2E\x99y\xe9z\\\\\xa1"
            b"\xc1\x8e\xee\xaeV\n\x99y%E\xf9\n\xd1\xba\x19\xb1\\\\\xfe\x01!\x9e"
            b"\xfe~\xc1\\\xba\x19\n\xfa\n\xba\xba\x19\xa99\x05\\\n@\xe0\x01d("
            b"\xe4\xa6\x16\x17'\xa6\xa7\x02\x00\xb6\xc3\x1a\xa8"
        )
        self.helpLOG         = (
            b"x\x9c\xf3M\xccKLOU(\xc9HU\xc8\xc9OWH\xcb\xccI\xd5\xe3\xe2\n\rvtw"
            b"\xb5\x02\x8bD\xebf\xc4\x02\x89d\x85\x1a\x05\xdd\xe2X..\xff\x80"
            b"\x10O\x7f\xbf`.\xa0\x88\xbe\x82\xaenrNjb\x11\x97\x02\x10\x84\x14"
            b"\x95\xe6%'\x96\xa0\x9a\xc5\xa5[\x0cVV\x9cY\x95\nV\xe5\x92Y\\\x90"
            b"\x93X\tV\x04\x12T\xc8OC\xd3\x90\x01\xd6\x90\x91\x9aS\x00\xd6\xe0"
            b"\x01d(\xe4\xa6\x16\x17\x03\x9d\t\x00d\xd33\xb9"
        )
        self.helpOOPS        = (
            b"x\x9c=\xcc1\x0e\xc20\x0cF\xe1\xdd\xa7\xf8\x0f@9\x00L\x0cU7\x90"
            b"\xa0\xdd\x1b\x11G\xb1\x94\xc6Q\xec\xdc\x1f\xc1\xc0\xf6\x86O\xef"
            b"\xc9S\x1f\x15\x9e\x19%\x98\xe3\xad\xc7\x11j\x84$\x88#\x05)\x1c"
            b"\xcfD\xdb\xeb\xb6\xcc\x17\xa86#\xba?\xd6\x99\xd6,\xf6\xd7Q\xd9P"
            b"\xd5a\xa35\xed\x0em.Z\xed\x8a\xa4\x1d\x99K;a\x18c\xff\xe6\xef\xb2"
            b"\x7f\x00\xb7\xe7)\xaf"
        )
        self.helpPWD         = (
            b"x\x9c\r\xc6\xbd\x0e@0\x14\x06\xd0\xfd>\xc5\xf7\x02e\xb7I\x08\x16"
            b"$\x98\xc4 \xdch\xe3\xa7\xcdmE\xbc=g:\x99\xf1\xee\x98_\x8f\xa0\x19"
            b"\xcb-\xc2W\xc0ce7\xd7\x86\xd5\x08/\xc1\xca\x1b\x11\r]Z\xe4\t\xdc"
            b"\xb3bTz\"j\xda\xbej\xea\x8e\x94F\x0c\xa54\x1f\x8e\xf0+\xff\xe0d"
            b"\xef\xe7\x8d?\xf0\xad\x1e\x16"
        )
        self.helpQUIT        = (
            b"x\x9cs\xad\xc8,)V(\xc9HU((\xcaO/J\xcc\xd5\xe3\xe2\n\rvtw\xb5R(,"
            b"\xcd,Q\x88\xd6\xcd\x88\xe5\xe2\xf2\x0f\x08\xf1\xf4\xf7\x0b\xe6"
            b"\xd2\xcdP\xd0W\xd0\xd5\xcdH\xcd)\xe0R\x00\x02\x0f C!7\xb5\xb881="
            b"\x15\x00V\xbf\x161"
        )
        self.helpREINCARNATE = (
            b"x\x9c\x1d\x8b\xb1\n\xc2@\x10D\xfb\xfd\x8a\xf9\x81\x8b\xbd\x9d"
            b"\x85D\x1b#F+\xb1X\xc2\xe0\x05\xccy\xec\xee\xff\xe3\xe2+\x86\xc7"
            b"\xc0\xbb\xd1C-\x1cQ\x89\xb5\x05\xad\x1bs\xd3\xff\x97\xebFt\xfb."
            b"t\x1fD\x1e\xf3a<\xeea\\\xdb\xa2\xd64\x88g\xa9/\x91\xe9z?O\x97YJ"
            b"\xc5\x0e\xa5T~\xba 9\xa5`\xcbX\xdf\xfc\x01\xf4\xae#>"
        )
        self.helpRELOAD      = (
            b"x\x9cs\xceIM,RH\xce\xcf\xcdM\xccKQHNL\xceHU\x00\xb1\x8aRs\xf2"
            b"\x13S`\x12\xc5z\\\\\xa1\xc1\x8e\xee\xaeV0\x89h\xdd\x8cX..\xff\x80"
            b"\x10O\x7f\xbf`.\xdd\x0c\x05}\x05]\xdd\x8c\xd4\x9c\x02.\x05 \xf0"
            b"\x002\x14rS\x8b\x8b\x13\xd3S\x017\xd2\x1e\xb5"
        )
        self.helpRUNPATH     = (
            b"x\x9c\x0b(\xca\xcc+Q(\xc9HU(H,\xc9PH+\xca\xcfU(\xcfH-J\x05\x8b"
            b"\x01\xe5R\x8b\n\x8aR\x81\xa4Bf\xb1BQi^^f^\xba\x1e\x17Wh\xb0\xa3"
            b"\xbb\xab\x15H\x00\xac-Z7#\x96\x8b\xcb? \xc4\xd3\xdf/\x98K7CA_AW"
            b"7#5\xa7\x80K\x01\x08<\x80\x0c\x85\xdc\xd4\xe2\xe2\xc4\xf4T\x00"
            b"\x84\xb6$\x86"
        )
        self.helpSET         = (
            b"x\x9cu\x8f\xb1\x0e\xc20\x0cDw\x7f\x85G\x18\x12v\xb6\x0eUa\xa0EM"
            b"\xcb\x82\x18\x82dH\xa5\xa6\xad\x92\xd0\x89\x8f\xc75\x12\x03\x82"
            b"\x0c\x91\x9dwg_\x0c\xa5\x88\xdd\x90(L\x81\xf8\xc6\xd9\x86\xce^{"
            b"\x8a\x1a\xa05Y\x91o1R\xc2\xb3r\x17\\\r\xd6\x13+\xfa\x07\xe1\x13"
            b"U@\xe9\xb5\xd6k\x80\xac.\xdaC^6\x06\x96G@>\xe5B\xc7\x1b&G\x9f"
            b"\xb1 n\xc1\'\x99\xf3\xcd\xa1:6\xfb\xaa4\xa0\x1cnP)G\xfd$\xf2\x1d"
            b"\x17\xe8)F{\'PQ \'\x13f8\xa1\x1d~\xfe\x038\xe6\"\r\xe4\xc7\xf9"
            b"\xbd\xb8\x96\xf2\x9f\xe1\x05\xdc\xe8U\xfa"
        )
        self.helpSTOP        = (
            b"x\x9c\r\xcb\xb1\n\x83@\x10\x84\xe1~\x9fb^\xe0bog!\xc6&\nj%\x16"
            b"\x0b\xd9xb\xf4\x8e\xdb\x0b\xe2\xdbg\xa7\xfa\xe1cz\xfe\xa9(\xb2"
            b"\x17\xc4\x14\xd6\xc4\x07\xf8|\xe3\xe2-+>!\xc18!\x07SQ5\xbb\xb1"
            b"\xcb\xfd \x9a\x86\xaa\xa9Kh\x0e\x11\xb3\xf3\x0bQ\xd7\x8fm\xf7\x1a"
            b"\xc8y\x14p\xce\xcb7\x12lO\x0b\x1c\xf6\xe6U\xfe?\x04#\x9a"
        )
        self.helpSTRIP       = (
            b"x\x9cm\x91\xbdN\x031\x0c\xc7\xf7<\x85_\xe0\x8e\x1d\xa6\x0eUa\xe0"
            b"\x8a\xb8\xeb\x84:\xa4\x89i\"\xa5I\x14\xfbTx{\x9c\xb4\x85\xb6\xe2"
            b"\x06\x9f?~\x7f\xdbrF.>\x13\x90\xfc\xe2\x9e }B@m\xc5\x07\x1d-p\xd1"
            b">\xd4\xe0\xe8<#em\x10\x8c\xd3E\x1b\xc6B\xbdR\x9bq\xb1Z>6y\x86\x8f"
            b"\xcem\xc5\xc4P-WC\xd5\x94m\xadC\xdf\x0b\xbfx_m^\x97\xc34*I)\x90o<"
            b"O\xe6\x04;<5\xcah\xeb\"\x7f3\x95Z\xbfM/\xebaTC\x8a\xa8\xc66M\x87"
            b"\xf0\xffZJ6\x80\x07\xe8\xba\x88GY\x1e\xe9wN\x86s\xea\x86\xe6\x06"
            b"\xb3\xde]\x83\x12\xde@\xd4\xa06\xea\x1a;\'\xba\xd2\xcaF\x97\xe2"
            b"\xf5\x1e\x0b\xf2\\\xe25w\xa9\xc0\xa9t\xd3\xda5\xad\xc3\x90\x9b"
            b"\xe0Y\x1c8 \x91\xe0J\r\xebi\xa9&\xe7\tL:\x1c\xea\x9b\x88\x1b\x13"
            b"\x83\x8f\x8c\xd1\xca\xa5N\x87\xc3/43Kh}A\xc3\xe1\xfb\t\xf8Nu\xa7"
            b"\x98I\xdc\xa3g\x07\x89\x1d\x96\x0b\xd9^\"\x97dg9j\x9a9\xcf\x0c"
            b"\x9a\xc0\"Ic\xdb\xff\x00\xac\xf5\xbcB"
        )
        self.helpTIME        = (
            b"x\x9cs\xc9,.\xc8I\xac,V(\xc9HUH.-*J\xcd+Q(\xae,.I\xcdU(\xc9\xcc"
            b"M\xd5\xe3\xe2\n\rvtw\xb5\x02\xf3\x14\xa2u3b\xb9\xb8\xfc\x03B<\xfd"
            b"\xfd\x82\xb9t3\x14\xf4\x15tu3Rs\n\xb8\x14\x80\xc0\x03\xc8P\xc8M-."
            b"NLO\x05\x002\xe7\x1b\xf8"
        )
        self.helpTIMEIT      = (
            b"x\x9c5\x8e\xb1\x0e\x830\x10C\xf7\xfb\noL\xf0\x01\xdd\x18\x10KK"
            b"\xa5\x02\x1f\x10\xe0hN\nIDB\xcb\xe77\x05\xe1\xcd\xd6\xdd\xb3;Y"
            b"\x18Q3x\xe7q\x8b\xe2,\xdc\x0c\x85\xd1-\x8b\xb2SA\xd4\xb7e]\xdd"
            b"\x10\xd3\xa1D\x18KT\xbe\xea\xfeQ5]K\xc9!\xe9.6A\x1c\x86\x0b\xc3"
            b"\x13Q\xf3\xec*\xca5\x12\x05y\xae\xd9x8\xff/\x08P+c\xb3\xea\xa3"
            b"\xc4\xa8\xc10f\xb7\xa6\r\x12\xaeVL\xdb\xc1K\xd6\x1b\x19\xd5\xf9"
            b"\xf5\x95\xa8\xe1\xd5\x1a\xc4\xbe\x0b\xea\x03#;\xa8\xe7\xb2\xec"
            b"\xa0H\x0c8C\xdec\xf1\x03m$J\x98"
        )
        self.helpTITLE       = (
            b"x\x9c}\x8d\xc1\x0e\xc2 \x10D\xef\xfb\x15\xfb\x03\xe8\xdd[c\x9a"
            b"\xeaAjJ{jz \xba\x02\t\xb2\x06\x88\xfc\xbe\x04=;\xa7\x99\xe4\xbd"
            b"\xcc\xd1\xea`(a\xb6\x84\xd9eO\xc8\x8f6n\x1c\x12\xd7Y\\\xb8s\xd9"
            b"\x01,\xaa\x1b\xfa\xc3\x0fZ\x85\xddpM9n\x00\xdd4,\x97^\xce\n$\x07"
            b"\x02\xac\x99\xe8M1cf\xe4\xe8\x8c\x0b\xda\x7f=\xa8F\x03$\x95\x7fw"
            b"\x00\xe3u>\x8fR\x81\xb0\xb8G!,\xf9W\x13O\xb5\xe0\x93R\xd2\x86>"
            b"\xc5\xeb<R"
        )
        self.helpVER         = (
            b"x\x9cs\xc9,.\xc8I\xac,V(\xc9HU(K-*\xce\xcc\xcfS\xc8OSp\xce\xcfM"
            b"-Q\xc8\xcc+I-*(J\x05\x92z\\\\\xa1\xc1\x8e\xee\xaeV U\n\xd1\xba"
            b"\x19\xb1\\\\\xfe\x01!\x9e\xfe~\xc1\\\xba\x19\n\xfa\n\xba\xba\x19"
            b"\xa99\x05\\\n@\xe0\x01d(\xe4\xa6\x16\x17'\xa6\xa7\x02\x00E{\x1e"
            b"\xe6"
        )
        self.helpWHEREIS     = (
            b"x\x9c\xf3\xc9ON,IUH\xce\xcf\xcdM\xccK)\xd6\xe3\xe2\n\rvtw\xb5R"
            b"(\xcfH-J\xcd,V\x88\xd6\xcd\x88\x85I+\xe8\xe9\x01\x158\x06\xb9\x87"
            b"\xfa\xba\xfa\x85\x04sA\x85\xb9\x14\x80\xc0/17U!?M\xa1$\x03n\x1a"
            b"\x17\x97\x7f@\x88\xa7\xbf_0\x97n\x86\x82\xbe\x82\xaenFjN\x01X\xb1"
            b"KfqANb\xa5\x02H@!7\xb5\xb881=\x15\x00\x98\xde*{"
        )


class BuiltInCmds(HelpTxts):
    """
    The command functions have the following parameters:
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Name of the command
    > param args: Arguments of the command
    > param opts: Options of the command
    > param fullComm: Full prompt line
    > param stream: Original stdout
    > param op: Operation next in line to be performed
    > param debug: Is debugging enabled?
    > return: Error code (ref. src\\errCodes.txt)
    """
    def __init__(self, intrp: "comet.Intrp", mainFlTitle: str) -> None:
        super().__init__()
        self.intrp       = intrp
        self.mainFlTitle = mainFlTitle

        self.ERR_PROTVAREDIT = 105
        self.ERR_NOSUCHVAR   = 106
        self.ERR_NOHELPSTR   = 107
        self.ERR_NOSUCHCMD   = 113
        self.ERR_CANTSORT    = 115
        self.ERR_DIDNTFAIL   = 116
        self.ERR_OOPSRERUN   = 117

    def ABOUT(self, varTable: dict[str, str], origPth: str, prevErr: int,
              cmd: str, args: dict[int, str], opts: dict[int, str],
              fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Displays the \"about\" of Comet."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}
        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpABOUT))
                return comm.ERR_SUCCESS
        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT
        print("Comet 1.0, developed by Infinite Inc.\n"
              "Written in Python 3.12.6")
        return comm.ERR_SUCCESS

    def BIN(self, varTable: dict[str, str], origPth: str, prevErr: int,
            cmd: str, args: dict[int, str], opts: dict[int, str],
            fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Displays the external commands (commands located in \"bin\") and their paths."
        toPrn: list[tuple[str, str]]
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}
        binDir    = os.path.join(origPth, "bin")
        toPrn     = []
        toPrnApp  = toPrn.append
        green     = comm.ANSIGREEN if op == '' else ''
        reset     = comm.ANSIRESET if op == '' else ''

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpBIN))
                return comm.ERR_SUCCESS

        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT

        try:
            maxLen = 0
            for item in os.scandir(binDir):
                if item.is_file():
                    justNm = os.path.splitext(item.name)[0]
                    maxLen = max(maxLen, len(justNm))
                    toPrnApp((justNm, item.path))

            if toPrn:
                print('\n'.join(f"{green}{i:<{maxLen}}{reset} {j}" for i, j in toPrn))

        except FileNotFoundError:
            pass

        return comm.ERR_SUCCESS

    def CACHE(self, varTable: dict[str, str], origPth: str, prevErr: int,
              command: str, args: dict[int, str], opts: dict[int, str],
              fullComm: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Displays the cached commands."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpCD))
                return comm.ERR_SUCCESS

        maxLen = max([len(k) for k in self.intrp.cache], default=0)
        for key in self.intrp.cache:
            print(f"{key:<{maxLen}} {self.intrp.cache[key]}")

        return comm.ERR_SUCCESS

    def CD(self, varTable: dict[str, str], origPth: str, prevErr: int,
           cmd: str, args: dict[int, str], opts: dict[int, str],
           fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Changes the current working directory."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'~', '!', 'h', "-help"}
        cwd       = os.getcwd()
        goTo      = ''
        homeDir   = False
        prevDir   = False

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpCD))
                return comm.ERR_SUCCESS

            for opt in optVals:
                if opt == '~':
                    homeDir = True
                elif opt == '!':
                    prevDir = True

        # NOTE: Note to self: From the Python docs:
        # Return an iterator that applies function to every item of iterable,
        # yielding the results.
        optRes = sum(map(bool, (homeDir, prevDir)))

        if optRes > 1:
            comm.ERR("Cannot cd to all the damn directories at the same time; specify one, you idiot")
            return comm.ERR_INCOPTUSAGE

        # First group: no args and no opts
        # Second group: both args and opts
        # Third group: more than one arg
        grp1 = not args and not (homeDir or prevDir)
        grp2 = args and optRes
        grp3 = len(args) >= 2
        if grp1 or grp2 or grp3:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT

        if homeDir:
            self.intrp.varTable["prevpth"] = cwd
            goTo                           = os.path.expanduser("~")

        elif prevDir:
            tmp2                           = self.intrp.varTable["prevpth"]
            self.intrp.varTable["prevpth"] = cwd
            goTo                           = tmp2

        else:
            pth = args[sorted(args)[0]]

            # Chk if the inp contains only slashes. If yes, then go to root
            # dir, else add a slash at the end of the inp, to counter the
            # effect of `cd C:` going to the dir previously in drive C
            if [i for i in pth if i not in ('\\', '/')]:
                pthTmp = pth + os.sep
            else:
                pthTmp = '\\'

            if os.path.isdir(pthTmp):
                self.intrp.varTable["prevpth"] = cwd
                goTo                           = pthTmp
            else:
                comm.ERR(f"No such directory: '{pth}'")
                return comm.ERR_NODIR

        try:
            os.chdir(goTo)
        except FileNotFoundError:
            comm.ERR("Race condition; directory modified before cd executed")
            return comm.ERR_RACECONDN
        except PermissionError:
            comm.ERR(f"Access is denied: \"{goTo}\"")
        except OSError:
            comm.ERR(f"Invalid argument: \"{goTo}\"")

        self.intrp.path = os.getcwd()
        return comm.ERR_SUCCESS

    def CLEAR(self, varTable: dict[str, str], origPth: str, prevErr: int,
              cmd: str, args: dict[int, str], opts: dict[int, str],
              fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Clears the output screen."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                return comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpCLEAR))
                return comm.ERR_SUCCESS

        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT

        os.system("cls")
        return comm.ERR_SUCCESS

    def COMET(self, varTable: dict[str, str], origPth: str, prevErr: int,
              cmd: str, args: dict[int, str], opts: dict[int, str],
              fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Displays information on the Comet interpreter."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpCOMET))
                return comm.ERR_SUCCESS

        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT

        print(comm.DECOMPSTR(
            b"x\x9cU\x8d\xb1\n\xc2@\x10D\xfb\xfb\x8a-\x15\xccE-\xed\xc4J\xb4S"
            b"\xb0\x94\xf3\xb2z\xab\xc9\xee\xb1\xd9\x04\xf2\xf7\x1e\x98\xc6ff"
            b"\x98\x19x\xd7\x84p\x90\x0e\r\x88\r5+\x16]\xc1\x88\xda\x930l\xfc"
            b"\xda\x1d$OJ\xafd\xb0\x88K8\xf2\x93\x98\x0cK\x88\xde\xdd\x94\xcc"
            b"\x90\xe11\xc15\x91\x0ech\xdb\"\x0c\xa7\xd0\x05\row\xa6\x88\x1c"
            b"\xb1\x81\x81\x1bT\xb0\x82\xdb\xe7\x10\x8bm\xfd\x1a\xe6\xd5]2F\n"
            b"m\x99\x03\x7fz0\x81\xac\xd2e\xbb\x9bH\xfb\xa1BNf\xb9\xdf\xd5\xf5"
            b"\x8b,\r\x0f\x1f\xa5\xab\x7f\x97j\xbe\xd4y\xb2$\\\xfd\xb7\xcb/"
            b"\xd9OQ\x08"
        ))
        return comm.ERR_SUCCESS

    def CMD(self, varTable: dict[str, str], origPth: str, prevErr: int,
            cmd: str, args: dict[int, str], opts: dict[int, str],
            fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Executes terminal commands."
        req: list[str]
        req = []

        for i in range(len(args) + len(opts)):
            if i in args:
                req.append(args[i])
            elif i in opts:
                req.append('-' + opts[i])

        sp.run(req, shell=True)

        # Revert to original title; may have changed during execution
        ct.windll.kernel32.SetConsoleTitleW(self.intrp.title)
        return comm.ERR_SUCCESS

    def CREDITS(self, varTable: dict[str, str], origPth: str, prevErr: int,
                cmd: str, args: dict[int, str], opts: dict[int, str],
                fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Displays credits."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}
        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpCREDITS))
                return comm.ERR_SUCCESS
        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT
        print("Developed by Infinite Inc.\n"
              "Written by Thiruvalluvan Kamaraj")
        return comm.ERR_SUCCESS

    def DATE(self, varTable: dict[str, str], origPth: str, prevErr: int,
             cmd: str, args: dict[int, str], opts: dict[int, str],
             fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Displays the current system date."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}
        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpDATE))
                return comm.ERR_SUCCESS
        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT
        print(dt.datetime.today().strftime("%d-%m-%Y"))
        return comm.ERR_SUCCESS

    def EXIT(self, varTable: dict[str, str], origPth: str, prevErr: int,
             cmd: str, args: dict[int, str], opts: dict[int, str],
             fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Exits the program."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpEXIT))
                return comm.ERR_SUCCESS

        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT

        # Blarghhh
        raise EOFError

    def GET(self, varTable: dict[str, str], origPth: str, prevErr: int,
            cmd: str, args: dict[int, str], opts: dict[int, str],
            fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Gets an interpreter variable's value."
        toPrn: list[str]
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}
        toPrn     = []
        toPrnApp  = toPrn.append
        err       = comm.ERR_SUCCESS

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_INCFORMAT
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpGET))
                return comm.ERR_SUCCESS

        if not args:
            for var in varTable:
                toPrnApp(f"{var}={repr(varTable[var])}")

        for arg in args.values():
            tmp2 = comm.DICTSRCH(arg, varTable, caseIn=True)
            if tmp2 is not None:
                toPrnApp(f"{arg}={repr(tmp2[0])}")
            else:
                comm.ERR(f"No such variable: '{arg}'")
                err = err or self.ERR_NOSUCHVAR

        if toPrn:
            print('\n'.join(toPrn))

        return err

    def _builtIn_gen_HELP_HELPER(self, usageInfo: bool) \
            -> tuple[list[str], list[str], int]:
        """
        Helper function of _gen_HELP_HELPER(). Gets the built-in commands and
        their help strings.
        > param usageInfo: True if the user had asked for usage to be displayed
        > return: Tuple of commands, their help strings and the maximum
                  length of the command strings
        """
        cmds       : list[str]
        cmdHelpStrs: list[str]
        maxLen      = 0
        cmds        = []
        cmdHelpStrs = []
        cmdApp      = cmds.append
        cmdHelpApp  = cmdHelpStrs.append

        for attr in dir(self):
            forbiddenCmds = {"ABIRAM", "AMIT", "NABHAN"}
            if not attr.isupper() or attr.startswith("ERR_") or attr in forbiddenCmds:
                continue

            maxLen = max(maxLen, len(attr))
            cmdApp(attr.lower())

            if not hasattr(self, "help" + attr):
                cmdHelpApp('-')
                continue

            helpBytes = getattr(self, "help" + attr)
            if not isinstance(helpBytes, bytes):
                comm.ERR(f"Invalid help string: '{attr.lower()}'", sl=5)
                cmdHelpApp("[INVALID]")
                continue

            helpStr      = zl.decompress(helpBytes).decode()
            helpStrSplit = helpStr.split('\n')

            if not usageInfo:
                cmdHelpApp(helpStrSplit[0])
            else:
                usageStr = next(
                    (i for i in helpStrSplit if i.startswith("USAGE: ")),
                    "[INVALID USAGE STR]"
                )
                cmdHelpApp(usageStr.removeprefix("USAGE: "))

        return cmds, cmdHelpStrs, maxLen

    def _ext_gen_HELP_HELPER(self, usageInfo: bool) \
            -> tuple[list[str], list[str], int]:
        """
        Helper function of _gen_HELP_HELPER(). Gets the external commands and
        their help strings.
        > param origPth: Path of the interpreter
        > return: Tuple of commands, their help strings and the maximum
                  length of the command strings
        """
        cmds       : list[str]
        cmdHelpStrs: list[str]
        maxLen      = 0
        cmds        = []
        cmdHelpStrs = []
        cmdApp      = cmds.append
        cmdHelpApp  = cmdHelpStrs.append

        try:
            for fl in os.scandir(comm.BINDIR):
                nm, ext = os.path.splitext(fl.name)
                if not (ext.lower() == ".py" or ext.lower() == ".pyd"):
                    continue

                try:
                    mod, err = comm.LDBINMOD(nm)
                    if err:
                        if err == -1:
                            comm.UNERR(f"Failed to import module: '{nm}'")
                        continue

                    if not hasattr(mod, nm.upper()):
                        continue
                    maxLen = max(maxLen, len(nm))
                    cmdApp(nm)

                    if hasattr(mod, "helpStr"):
                        helpStr = getattr(mod, "helpStr")

                        if not isinstance(helpStr, bytes):
                            comm.ERR(f"Invalid help string: '{nm.lower()}'",
                                     sl=5)
                            continue

                        helpStr = comm.DECOMPSTR(helpStr)

                        if not usageInfo:
                            cmdHelpApp(helpStr.split('\n')[0])
                        else:
                            usageStr = next(
                                (i for i in helpStr if i.upper().startswith("USAGE: ")),
                                "[INVALID USAGE STR]"
                            )
                            cmdHelpApp(usageStr.removeprefix(usageStr[8:]))

                    else:
                        cmdHelpApp('-')

                except FileNotFoundError:
                    comm.INFO("Whoa. Command file was pulled out right from "
                              f"under the interpreter! \"{nm}\"")

                except (AttributeError, ImportError):
                    comm.INFO("Filename suggests a command file, but necessary "
                              "conditions to be a command were not satisfied. "
                              "Please check")

        # Dir "bin" does not exist
        except FileNotFoundError:
            pass

        return cmds, cmdHelpStrs, maxLen

    def _gen_HELP_HELPER(self, origPth: str, usageInfo: bool, green: str,
                         reset: str, op: str) -> int:
        """
        Displays all commands and their help strings.
        > param origPth: Path of the interpreter
        > return: Error code (ref. src\\errCodes.txt)
        """
        toPrn: list[str]
        toPrn      = []
        toPrnApp   = toPrn.append
        err        = comm.ERR_SUCCESS

        bltInComms = self._builtIn_gen_HELP_HELPER(usageInfo)
        extComms   = self._ext_gen_HELP_HELPER(usageInfo)
        maxLen     = max(bltInComms[2], extComms[2])

        cmds        = bltInComms[0] + extComms[0]
        cmdHelpStrs = bltInComms[1] + extComms[1]

        cmds, cmdHelpStrs, err = comm.SORTTWOARRS(cmds, cmdHelpStrs)
        if err == 1:
            comm.CRIT("Unable to sort commands; arrays were of different lengths",
                      raiser='c', sl=5)
            err = self.ERR_CANTSORT

        for i, name in enumerate(cmds):
            toPrnApp(f"{green}{name.lower():<{maxLen}}{reset} {cmdHelpStrs[i]}")

        if toPrn:
            print('\n'.join(toPrn))
        return err

    def _ext_spec_HELP_HELPER(self, origPth: str, arg: str) \
            -> tuple[str, int]:
        """
        Helper function for _spec_HELP_HELPER(). Displays the help message
        for a specific external command.
        > param origPth: Path of the interpreter
        > return: Tuple of help string and error code (ref. src\\errCodes.txt)
        """
        try:
            binPth  = os.path.join(origPth, "bin")
            pyNm    = str(pl.Path(os.path.join(binPth, arg + ".py")).resolve())
            pydNm   = str(pl.Path(os.path.join(binPth, arg + ".pyd")).resolve())
            pyBase  = os.path.basename(pyNm)
            pydBase = os.path.basename(pydNm)
            nm, _   = os.path.splitext(pyBase if os.path.isfile(pyNm) else pydBase)

            for item in os.scandir(binPth):
                if os.path.isdir(item):
                    continue
                if not (item.name.endswith(".py") or item.name.endswith(".pyd")):
                    continue

                itemNm, _ = os.path.splitext(item.name)
                if itemNm.lower() != nm.lower():
                    continue

                try:
                    mod = il.import_module("bin." + nm, package="bin")
                    il.reload(mod)

                    # Module MUST have a func with cmd name in uppercase to
                    # be recognised as a cmd
                    if not hasattr(mod, nm.upper()):
                        continue
                    if hasattr(mod, "helpStr"):
                        tmp = getattr(mod, "helpStr")
                        break
                    else:
                        comm.ERR(f"No help string available: \"{arg}\"")
                        return '', self.ERR_NOHELPSTR

                except FileNotFoundError:
                    pass

            else:
                comm.ERR(f"No such command: \"{arg}\"", sl=5)
                return '', self.ERR_NOSUCHCMD

        # Directory "bin" was not found
        except FileNotFoundError:
            comm.ERR(f"No such command: \"{arg}\"", sl=5)
            return '', self.ERR_NOSUCHCMD

        return tmp, comm.ERR_SUCCESS

    def _spec_HELP_HELPER(self, origPth: str, arg: str) -> int:
        """
        Displays the help message for a specific command.
        > param origPth: Path of the interpreter
        > param arg: A string to fetch the help string for
        > return: Error code (ref. src\\errCodes.txt)
        """
        cmdFound  = False
        helpFound = False

        if arg.lower() == "please":
            print(";)")
            return 0

        if hasattr(self, arg.upper()):
            cmdFound = True
        if hasattr(self, "help" + arg.upper()):
            helpFound = True

        if cmdFound and helpFound:
            print(f"COMMAND: {arg.lower()}")
            print('\n'.join(
                line.expandtabs(4)
                for line in getattr(self, "help" + arg.upper())
            ))
            return comm.ERR_SUCCESS

        tmp = self._ext_spec_HELP_HELPER(origPth, arg)
        if tmp[1] != 0:
            if cmdFound and not helpFound:
                comm.INFO(f"Built-in command found but help string was not: '{arg}'",
                          sl=4)
            elif not cmdFound and helpFound:
                comm.INFO(f"Command not found; but built-in help string found: '{arg}'",
                          sl=4)
            return tmp[1]

        print(f"COMMAND: {arg.lower()}")
        print('\n'.join(line.expandtabs(4) for line in tmp[0]))
        return comm.ERR_SUCCESS

    def HELP(self, varTable: dict[str, str], origPth: str, prevErr: int,
             cmd: str, args: dict[int, str], opts: dict[int, str],
             fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Displays the main help messages, and command-specific help messages."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'s', 'u', 'h',
                     "-syntax", "-usage", "-help"}
        usageInfo = False
        err       = comm.ERR_SUCCESS
        green     = comm.ANSIGREEN if op == '' else ''
        reset     = comm.ANSIRESET if op == '' else ''

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpHELP))
                return comm.ERR_SUCCESS
            for opt in optVals:
                if opt == 's' or opt == "-syntax" or opt == 'u' or opt == "-usage":
                    if args:
                        comm.ERR(f"Cannot use -{opt} when supplying arguments")
                        return 3
                    usageInfo = True

        if not args:
            err = self._gen_HELP_HELPER(origPth, usageInfo, green, reset, op)
        else:
            argsFinIdx = len(args) - 1
            for i, arg in enumerate(args.values()):
                tmp2 = self._spec_HELP_HELPER(origPth, arg)
                err  = err or tmp2
                print() if i < argsFinIdx and not err else None

        return err

    def INTRO(self, varTable: dict[str, str], origPth: str, prevErr: int,
              cmd: str, args: dict[int, str], opts: dict[int, str],
              fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Displays the intro message."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}
        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpINTRO))
                return comm.ERR_SUCCESS
        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT
        print(self.intrp.introTxt)
        return comm.ERR_SUCCESS

    def LOG(self, varTable: dict[str, str], origPth: str, prevErr: int,
            cmd: str, args: dict[int, str], opts: dict[int, str],
            fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Manage the log file."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'c', 's', 'h', "-clear", "-size", "-help"}
        clear     = False
        size      = False
        err       = comm.ERR_SUCCESS

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpLOG))
                return comm.ERR_SUCCESS

            for opt in optVals:
                if opt in ('c', "-clear"):
                    if size:
                        comm.ERR("Cannot accept both clear and size options at the same time")
                        return comm.ERR_INCOPTUSAGE
                    clear = True
                elif opt in ('s', "-size"):
                    if clear:
                        comm.ERR("Cannot accept both clear and size options at the same time")
                        return comm.ERR_INCOPTUSAGE
                    size = True

        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT

        if size:
            try:
                print(os.path.getsize(comm.LOGFL))
            except Exception:
                comm.CRIT("Unhandled exception while attempting to get size of log file")
                err = comm.ERR_UNKNOWN

        elif clear:
            try:
                with open(comm.LOGFL, 'w', buffering=1) as f:
                    f.truncate(0)
            except PermissionError:
                comm.ERR(f"Access is denied: \"{comm.LOGFL}\"")
                err = comm.ERR_PERMDENIED

        else:
            try:
                with open(comm.LOGFL, 'r', buffering=1) as f:
                    for ln in f:
                        print(ln, end='')
            except PermissionError:
                comm.ERR(f"Access is denied: \"{comm.LOGFL}\"")
                err = comm.ERR_PERMDENIED
            except FileNotFoundError:
                # Should never happen. The interpreter wouldn't start if it
                # is unable to create the log file and have access to it. But,
                # I've put this check, just in case, cause I'm incompetent
                comm.ERR(f"Log file \"{comm.LOGFL}\" was not found. That is not supposed to happen")
                err = comm.ERR_NOFL
            except UnicodeDecodeError:
                comm.ERR(f"Does not appear to contain text: \"{comm.LOGFL}\"")
                err = comm.ERR_CANTDECODE

        return err

    def OOPS(self, varTable: dict[str, str], origPth: str, prevErr: int,
             cmd: str, args: dict[int, str], opts: dict[int, str],
             fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        """
        Re-run the last command if it failed, i.e. non-zero error code.
        Note that this command ignore all options and arguments passed so that
        those error codes do not clash with the failed command being
        re-executed.
        """
        lastCmd = self.intrp.lastCmd

        if debug:
            comm.INFO("Last command: " + repr(lastCmd))

        if not self.intrp.err:
            comm.ERR(f"Last command did NOT fail; error code {self.intrp.err}")
            return self.ERR_DIDNTFAIL

        if self.intrp.parse(lastCmd)[0][0].lower() == "oops":
            comm.ERR("Cannot re-run command oops")
            return self.ERR_OOPSRERUN

        return self.intrp.execute(lastCmd)

    def PRITH(self, varTable: dict[str, str], origPth: str, prevErr: int,
              cmd: str, args: dict[int, str], opts: dict[int, str],
              fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Prints out another fact."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpPWD))
                return comm.ERR_SUCCESS

        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT

        print("Prith is a BAKA!")
        return comm.ERR_SUCCESS

    def PWD(self, varTable: dict[str, str], origPth: str, prevErr: int,
            cmd: str, args: dict[int, str], opts: dict[int, str],
            fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Prints the current working directory."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}
        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpPWD))
                return comm.ERR_SUCCESS
        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT
        print(self.intrp.path)
        return comm.ERR_SUCCESS

    def QUIT(self, varTable: dict[str, str], origPth: str, prevErr: int,
             cmd: str, args: dict[int, str], opts: dict[int, str],
             fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Quits the program."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpQUIT))
                return comm.ERR_SUCCESS

        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT

        raise EOFError

    def REINCARNATE(self, varTable: dict[str, str], origPth: str, prevErr: int,
                    cmd: str, args: dict[int, str], opts: dict[int, str],
                    fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Restarts the interpreter in the same process."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpREINCARNATE))
                return comm.ERR_SUCCESS

        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT

        raise comm.SIGREINCARNATE()

    def RELOAD(self, varTable: dict[str, str], origPth: str, prevErr: int,
               cmd: str, args: dict[int, str], opts: dict[int, str],
               fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Clear command cache and reload commands."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpRELOAD))
                return comm.ERR_SUCCESS

        if not args:
            self.intrp.cache.clear()

        for arg in args.values():
            res = comm.DICTSRCH(arg, self.intrp.cache, caseIn=True,
                                returnMode="keys")
            if not res:
                continue
            self.intrp.cache.pop(res[0])

        return comm.ERR_SUCCESS

    def RUNPATH(self, varTable: dict[str, str], origPth: str, prevErr: int,
                cmd: str, args: dict[int, str], opts: dict[int, str],
                fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Displays the path Comet is running from."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpRUNPATH))
                return comm.ERR_SUCCESS

        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT

        print(origPth)
        return comm.ERR_SUCCESS

    def _set_SET_HELPER(self, args: dict[int, str], protected: set[str]) -> int:
        """
        Helper function for the set feature of the set command.
        > param args: Dictionary of arguments
        > return: Error code (ref. src\\errCodes.txt)
        """
        if len(args) != 2:
            comm.ERR("Incorrect format", sl=4)
            return comm.ERR_INCFORMAT

        arg = comm.LOWERLT(args)[0]
        if arg in protected:
            comm.ERR("Operation not allowed; cannot edit "
                     "var 'error'", sl=4)
            return self.ERR_PROTVAREDIT

        sortedArgs = sorted(args)
        varName    = args[sortedArgs[0]]
        varVal     = args[sortedArgs[1]]

        if keys := comm.DICTSRCH(varName, self.intrp.varTable,
                                 caseIn=True, returnMode="keys"):
            for key in keys:
                self.intrp.varTable.pop(key)

        self.intrp.varTable[varName] = varVal
        return comm.ERR_SUCCESS

    def _rm_SET_HELPER(self, args: dict[int, str], protected: set[str]) -> int:
        """
        Helper function for the remove feature of the set command.
        > param args: Dictionary of arguments
        > return: Error code (ref. src\\errCodes.txt)
        """
        err = comm.ERR_SUCCESS

        if not args:
            comm.ERR("Incorrect format", sl=4)
            return comm.ERR_INCFORMAT

        for arg in args.values():
            if arg.lower() in protected:
                comm.ERR("Operation not allowed; cannot "
                         "remove var 'error'", sl=4)
                err = err or self.ERR_PROTVAREDIT
                continue

            if not (keys := comm.DICTSRCH(arg, self.intrp.varTable,
                                          caseIn=True, returnMode="keys")):
                comm.ERR(f"No such variable: '{arg}'", sl=4)
                err = err or self.ERR_NOSUCHVAR
                continue

            for key in keys:
                self.intrp.varTable.pop(key)

        return err

    def SET(self, varTable: dict[str, str], origPth: str, prevErr: int,
            cmd: str, args: dict[int, str], opts: dict[int, str],
            fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Sets interpreter variables."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'r', 'h', "-remove", "-help"}
        remove    = False
        # All entries must be in lowercase
        protected = {"error", "ud"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpSET))
                return comm.ERR_SUCCESS
            for opt in optVals:
                if opt == 'r' or opt == '-remove':
                    remove = True

        if not args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT

        if not remove:
            return self._set_SET_HELPER(args, protected)
        else:
            return self._rm_SET_HELPER(args, protected)

    def STOP(self, varTable: dict[str, str], origPth: str, prevErr: int,
             cmd: str, args: dict[int, str], opts: dict[int, str],
             fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Pauses the interpreter and waits for user to press any key."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpSTOP))
                return comm.ERR_SUCCESS

        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT

        stream.write("Input a key to continue: ")
        stream.flush()
        key = ms.getch()
        while ms.kbhit():
            ms.getch()
        stream.write(str(ord(key)) + '\n')
        stream.flush()
        return comm.ERR_SUCCESS

    def STRIP(self, varTable: dict[str, str], origPth: str, prevErr: int,
              cmd: str, args: dict[int, str], opts: dict[int, str],
              fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Strips strings of leading and trailing whitespace characters."
        toPrn: list[str]
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {"nl", 't', 's', 'r', 'h',
                     "-newlines", "-tabs", "-spaces", "-carriagereturns",
                     "-help"}
        nls       = False
        tabs      = False
        spaces    = False
        carrRets  = False
        toPrn     = []
        toPrnApp  = toPrn.append

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpSTRIP))
                return comm.ERR_SUCCESS

            for opt in optVals:
                if opt in ("nl", "-newlines"):
                    nls = True
                elif opt in ('t', "-tabs"):
                    tabs = True
                elif opt in ('s', "-spaces"):
                    spaces = True
                elif opt in ('r', "-carriagereturns"):
                    carrRets = True

        else:
            nls      = True
            tabs     = True
            spaces   = True
            carrRets = True

        if not args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT

        stripStr  = ''
        stripStr += '\n' if nls      else ''
        stripStr += '\t' if tabs     else ''
        stripStr += ' '  if spaces   else ''
        stripStr += '\r' if carrRets else ''

        for arg in args.values():
            arg = arg.strip(stripStr)
            toPrnApp(arg)

        if toPrn:
            print(''.join(toPrn), end='')

        return comm.ERR_SUCCESS

    def TIME(self, varTable: dict[str, str], origPth: str, prevErr: int,
             cmd: str, args: dict[int, str], opts: dict[int, str],
             fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Displays the current system time."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpTIME))
                return comm.ERR_SUCCESS

        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT

        print(dt.datetime.now().strftime('%H:%M.%S.%f'))
        return comm.ERR_SUCCESS

    def TIMEIT(self, varTable: dict[str, str], origPth: str, prevErr: int,
               cmd: str, args: dict[int, str], opts: dict[int, str],
               fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Time the execution of a command."
        green = comm.ANSIGREEN if op == '' else ''
        reset = comm.ANSIRESET if op == '' else ''

        actualCmd = fullCmd.lstrip().removeprefix(cmd)

        start  = ti.default_timer()
        self.intrp.execute(actualCmd)
        elapsed = ti.default_timer() - start

        print(f"elapsed {green}{round(elapsed, 6)}s{reset}")
        return comm.ERR_SUCCESS

    def TITLE(self, varTable: dict[str, str], origPth: str, prevErr: int,
              cmd: str, args: dict[int, str], opts: dict[int, str],
              fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Sets the title of the console window."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpTITLE))
                return comm.ERR_SUCCESS

        if not args:
            self.intrp.title = self.mainFlTitle
        elif len(args) != 1:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT
        for arg in args.values():
            self.intrp.title = arg

        ct.windll.kernel32.SetConsoleTitleW(self.intrp.title)
        return comm.ERR_SUCCESS

    def VER(self, varTable: dict[str, str], origPth: str, prevErr: int,
            cmd: str, args: dict[int, str], opts: dict[int, str],
            fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Displays the version of the Comet interpreter."
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}
        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpVER))
                return comm.ERR_SUCCESS
        if args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT
        print(self.intrp.version)
        return comm.ERR_SUCCESS

    def WHEREIS(self, varTable: dict[str, str], origPth: str, prevErr: int,
                cmd: str, args: dict[int, str], opts: dict[int, str],
                fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
        "Locate commands."
        toPrn: list[tuple[str, str]]
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}
        err       = comm.ERR_SUCCESS
        toPrn     = []
        toPrnApp  = toPrn.append

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return comm.ERR_UNKNOPTS
            if 'h' in optVals or "-help" in optVals:
                print(comm.DECOMPSTR(self.helpWHEREIS))
                return comm.ERR_SUCCESS

        if not args:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT

        builtInCmds = [i for i in dir(self.intrp.builtInCmds) if i.isupper()]
        binDir      = os.path.join(origPth, "bin")
        dirCntnts   = []
        maxLen      = 0
        if os.path.isdir(binDir):
            dirCntnts = [i for i in os.scandir(binDir)]

        for arg in args.values():
            if arg.upper() in builtInCmds and not arg.startswith("ERR_"):
                toPrnApp((arg, "Built-in"))
                maxLen = max(maxLen, len(arg))
                continue

            for item in dirCntnts:
                if os.path.isdir(item):
                    continue

                nm, ext = os.path.splitext(os.path.basename(item.path))
                if ext not in (".py", ".pyd"):
                    continue
                if nm.lower() != arg.lower():
                    continue

                try:
                    sys.path.insert(1, binDir)
                    mod = il.import_module("bin." + nm, package="bin")
                    sys.path.pop(1)
                    il.reload(mod)

                    if hasattr(mod, arg.upper()):
                        toPrnApp((arg, f"{item.path}"))
                        maxLen = max(maxLen, len(arg))
                        break

                except ImportError:
                    pass

            else:
                comm.ERR(f"No such (valid) command: \"{arg}\"")
                err = err or self.ERR_NOSUCHCMD

        padding = maxLen if op == '' else 0
        if toPrn:
            print('\n'.join(f"{i[0]:<{padding}} {i[1]}" for i in toPrn))
        return err
