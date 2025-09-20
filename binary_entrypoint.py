"""
PyInstallerでバイナリビルドするときのエントリーポイント
"""

import asyncio

from aoirint_matvtool.cli import main

if __name__ == "__main__":
    asyncio.run(main())
