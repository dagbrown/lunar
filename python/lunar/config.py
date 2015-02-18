#!/usr/bin/python

from wordexp import wordexp
import re
import os

#               DEFAULT="\e[0m"
#                  BOLD="\e[1m"
#                 BLACK="\e[30m"
#                   RED="\e[31m"
#                 GREEN="\e[32m"
#                YELLOW="\e[33m"
#                  BLUE="\e[34m"
#                VIOLET="\e[35m"
#                  CYAN="\e[36m"
#                 WHITE="\e[37m"
#
#          MODULE_COLOR="${WHITE}${BOLD}\e[40m"
#         VERSION_COLOR="${WHITE}${BOLD}\e[40m"
#           QUERY_COLOR="${YELLOW}${BOLD}"
#             LRM_COLOR="${YELLOW}${BOLD}"
#           CHECK_COLOR="${CYAN}"
#       RESURRECT_COLOR="${GREEN}${BOLD}"
#            FILE_COLOR="${GREEN}${BOLD}"
#         SYMLINK_COLOR="${CYAN}${BOLD}"
#         PROBLEM_COLOR="${RED}${BOLD}"
#         MESSAGE_COLOR="${CYAN}"
#         DEFAULT_COLOR="${DEFAULT}"
#
#         TAB_ENTER_IFS=$'\t\n'
#         ENTER_IFS=$'\n'
#         STANDARD_IFS=$' \t\n'


class Config:
  defaults = {
    "CONFIG_CACHE": "/etc/lunar/local",
    "LOCAL_CONFIG": "/etc/lunar/local/config",
    "DEPENDS_CONFIG": "/etc/lunar/local/depends",
    "LOCAL_EXCLUDED": "/etc/lunar/local/excluded",
    "MIRRORS": "/etc/lunar/mirrors",
    "LUNAR_MODULES": "lunar theedge",
    "MOONBASE_TYPES": "stable unstable",
    "BUILD_DIRECTORY": "/usr/src",
    "DOCUMENT_DIRECTORY": "/usr/share/doc",
    "DEFAULT_PREFIX": "/usr",
    "BOOTSTRAP": "/var/lib/lunar/bootstrap",
    "EXCLUDED": "/var/lib/lunar/excluded",
    "MOONBASE": "/var/lib/lunar/moonbase",
    "PROTECTED": "/var/lib/lunar/protected",
    "SOLO": "/var/lib/lunar/solo",
    "FUNCTIONS": "/var/lib/lunar/functions",
    "PYTHON": "/var/lib/lunar/python",
    "MENUS": "/var/lib/lunar/menu",
    "SUSTAINED": "/var/lib/lunar/sustained",
    "PLUGIN_DIR": "/var/lib/lunar/plugins",
    "SOUND_DIRECTORY": "/var/lib/lunar/sound",
    "SOUND_THEME": "startrek",
    "ACTIVITY_LOG": "/var/log/lunar/activity",
    "INSTALL_LOGS": "/var/log/lunar/install",
    "COMPILE_LOGS": "/var/log/lunar/compile",
    "MD5SUM_LOGS": "/var/log/lunar/md5sum",
    "INSTALL_QUEUE": "/var/log/lunar/queue/install",
    "REMOVE_QUEUE": "/var/log/lunar/queue/remove",
    "COMPRESS_METHOD": "xz",
    "DEPENDS_STATUS": "/var/state/lunar/depends",
    "DEPENDS_STATUS_BACKUP": "/var/state/lunar/depends.backup",
    "DEPENDS_CACHE": "/var/state/lunar/depends.cache",
    "MODULE_STATUS": "/var/state/lunar/packages.db",
    "MODULE_STATUS_BACKUP": "/var/state/lunar/packages.backup",
    "MODULE_INDEX": "/var/state/lunar/module.index.db",
    "INSTALL_CACHE": "/var/cache/lunar",
    "GNU_URL": "ftp://ftp.gnu.org/pub/gnu",
    "KDE_URL": "ftp://ftp.kde.org/pub/kde",
    "GNOME_URL": "ftp://ftp.gnome.org/pub/GNOME",
    "KERNEL_URL": "ftp://ftp.kernel.org",
    "SFORGE_URL": "http://downloads.sourceforge.net/sourceforge",
    "XFREE86_URL": "ftp://ftp.xfree86.org/pub/XFree86",
    "XORG_URL": "ftp://ftp.freedesktop.org/pub/xorg",
    "LRESORT_URL": "http://download.lunar-linux.org/lunar/cache",
    "MOONBASE_URL": [ "http://lunar-linux.org/lunar/", "http://download.lunar-linux.org/lunar/" ],
    "PATCH_URL": "http://download.lunar-linux.org/lunar/patches/",
    "MIRROR_URL": "http://download.lunar-linux.org/lunar/mirrors/",
    "TRACKED": "/bin /boot /etc /lib /sbin /usr /var /opt/lunar",
    "LUNAR_PRIORITY": "+10",
    # These ones can be changed by exporting an environment variable
    "SOURCE_CACHE": wordexp("${SOURCE_CACHE:-/var/spool/lunar}")[0],
    "ARCHIVE": wordexp("${ARCHIVE:-on}")[0],
    "AUTOFIX": wordexp("${AUTOFIX:-on}")[0],
    "AUTOPRUNE": wordexp("${AUTOPRUNE:-on}")[0],
    "MAIL_REPORTS": wordexp("${MAIL_REPORTS:-off}")[0],
    "PRESERVE": wordexp("${PRESERVE:-on}")[0],
    "REAP": wordexp("${REAP:-on}")[0],
    "ADMIN": wordexp("${ADMIN:-root}")[0],
    "SOUND": wordexp("${SOUND:-off}")[0],
    "SUSTAIN": wordexp("${SUSTAIN:-on}")[0],
    "VIEW_REPORTS": wordexp("${VIEW_REPORTS:-off}")[0],
    "VOYEUR": wordexp("${VOYEUR:-on}")[0],
    "GARBAGE": wordexp("${GARBAGE:-on}")[0],
    "PROMPT_DELAY": wordexp("${PROMPT_DELAY:-150}")[0],
    "PROBE_EXPIRED": wordexp("${PROBE_EXPIRED:-on}")[0],
    "LDD_CHECK": wordexp("${LDD_CHECK:-on}")[0],
    "FIND_CHECK": wordexp("${FIND_CHECK:-on}")[0],
    "MD5SUM_CHECK": wordexp("${MD5SUM_CHECK:-on}")[0],
    "SYM_CHECK": wordexp("${SYM_CHECK:-off}")[0],
    "TMPDIR": wordexp("${TMPDIR:-/tmp}")[0]
  }

  def __init__(self, config="/etc/lunar/local/config"):
    """
    Load up the configuration from /etc/lunar/config
    or whatever alternative location you give it
    """
    self.config = defaults

    os.putenv("PATH", "/sbin:/bin:/usr/sbin:/usr/bin:/usr/X11/bin")
    os.putenv("DIALOGRC", "/etc/lunar/dialogrc")

    lines=file(config,"r").read().split("\n")

    for line in lines:
      if re.search("^ *$", line):
        continue
      if re.search('^ *#.*$', line):
        continue
      words=wordexp(line)
      if len(words) == 0:
        next
      if words[0] == 'export':
        env, value = words[1].split("=")
        os.environ[env]=value
      else:
        variable, value = words[0].split("=")
        self.config[variable] = value

  def __getitem__(self, item):
    if self.config.has_key(item):
      return self.config[item]
    else:
      return None

config = Config()
