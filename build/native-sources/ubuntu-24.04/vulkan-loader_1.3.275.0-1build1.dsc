-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512

Format: 3.0 (quilt)
Source: vulkan-loader
Binary: libvulkan1, libvulkan-dev
Architecture: linux-any
Version: 1.3.275.0-1build1
Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
Uploaders: Timo Aaltonen <tjaalton@debian.org>
Homepage: https://github.com/KhronosGroup/Vulkan-Loader
Standards-Version: 4.5.0
Vcs-Browser: https://salsa.debian.org/xorg-team/vulkan/vulkan-loader
Vcs-Git: https://salsa.debian.org/xorg-team/vulkan/vulkan-loader.git
Testsuite: autopkgtest
Testsuite-Triggers: build-essential, pkg-config
Build-Depends: debhelper-compat (= 12), cmake, googletest <!nocheck>, libwayland-dev, libx11-dev, libxcb1-dev, libxrandr-dev, pkg-config, python3
Package-List:
 libvulkan-dev deb libdevel optional arch=linux-any
 libvulkan1 deb libs optional arch=linux-any
Checksums-Sha1:
 7295569482af305619609300bb2468a21fb39ac3 2642760 vulkan-loader_1.3.275.0.orig.tar.xz
 294bcd14216956146d6324be8afafb75d5718d80 9132 vulkan-loader_1.3.275.0-1build1.debian.tar.xz
Checksums-Sha256:
 5f95219fc189b4c09ce537d8ec1ea4b5861b087cd00b6d821f99aecf6e9dddce 2642760 vulkan-loader_1.3.275.0.orig.tar.xz
 16b22d9a95fb35ae1e9d9d89f26b4f27305f86700b20615c23618014ab184ac9 9132 vulkan-loader_1.3.275.0-1build1.debian.tar.xz
Files:
 6d1907a69c5218d29b917c7700fd7fc2 2642760 vulkan-loader_1.3.275.0.orig.tar.xz
 0b7703d20dcb7855ac513fa432d82584 9132 vulkan-loader_1.3.275.0-1build1.debian.tar.xz
Original-Maintainer: Debian X Strike Force <debian-x@lists.debian.org>

-----BEGIN PGP SIGNATURE-----

iQJHBAEBCgAxFiEET7WIqEwt3nmnTHeHb6RY3R2wP3EFAmYUGdMTHGp1bGlhbmtA
dWJ1bnR1LmNvbQAKCRBvpFjdHbA/ceP0EACaZgrUZG5L/YL2InMAi0oeznj001KD
BKRuL/GaCR4TxUBKk+uwro6gVZDlvwsnd8j76vrERR6FBih7YPpKRHtHolRf7gw3
/nrG6PfJlqAcg7kM+140c0L6INQhjyjVItkOp353mTu5PfKIoRnvVCDugyXMHrYJ
ValKMEnXsOmcEE0/uBRRZ/RNixnRSTUjyzRb5pjusimn5pXvHIoOJndf0r6yAy4P
GyzX+VXcYOHpHoJ9CMn4aimgOuGuIV3iS7gcmBCtidUqTsOwZWW3FtW8KnwurW/H
k9j8yMxCXvCuaIC4YtHC1a86JfOqsvy8LZomQqrGgaYiJ8F+ry+rEPkMT+9Yf/Bc
1U30qf5B8IOmM9jJJYfsyhgZlTL5o7J3z4CjxE1gAzefhPz6g35Le+O1ssrEVzm9
iYbqXDbLbk9v3IeU1kUWWeX0VsyBC0vdAMrFII2f9qUTY9CyD+Ym7MuHQjiMH0Vi
/rsJxxuJ7P2lmSQSrHDO8BejHfVeEeVPTnmUzLdg7xtVWweZ6plw8uK0dke/O6q9
CNsyYTTFX1ycIkWVyySCRZtBMHgOiT8cjCUJuR8r8EyYuUcI3hw3E6/A35LjGVJ8
FZ2OPMw4cddStC4zoh8MBOJL3YklRL0wcABOkjA7PgHFS3cTioHXIRTFRi4KTf1Z
ml/j9GE9+G2/rA==
=HunQ
-----END PGP SIGNATURE-----
