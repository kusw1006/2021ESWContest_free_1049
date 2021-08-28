# install_sequitur.sh 수정

>작성자: 이찬현
>
>작성일지: 21.08.28 20:21

```shell
#!/usr/bin/env bash

GIT=${GIT:-git}

set -u
set -e


# Make sure we are in the tools/ directory.
if [ `basename $PWD` == extras ]; then
  cd ..
fi


! [ `basename $PWD` == tools ] && \
  echo "You must call this script from the tools/ directory" && exit 1;

# Install python-devel package if not already available
# first, makes sure distutils.sysconfig usable
if ! $(python -c "import distutils.sysconfig" &> /dev/null); then
    echo "$0: WARNING: python library distutils.sysconfig not usable, this is necessary to figure out the path of Python.h." >&2
    echo "Proceeding with installation." >&2
else
  # get include path for this python version
  INCLUDE_PY=$(python -c "from distutils import sysconfig as s; print(s.get_python_inc())")
  if [ ! -f "${INCLUDE_PY}/Python.h" ]; then
      echo "$0 : ERROR: python-devel/python-dev not installed" >&2
      if which yum >&/dev/null; then
        # this is a red-hat system
        echo "$0: we recommend that you run (our best guess):"
        echo " sudo yum install python-devel"
      fi
      if which apt-get >&/dev/null; then
        # this is a debian system
        echo "$0: we recommend that you run (our best guess):"
        echo " sudo apt-get install python-dev"
      fi
      exit 1
  fi
fi

command -v swig >/dev/null 2>&1 || {
  echo >&2 "$0: Error: I require swig but it's not installed.";
  echo >&2 "  Please install swig and run this script again. "
  exit 1;
}

if [ -d ./g2p ] || [ -d sequitur ] ; then
  echo  >&2 "$0: Warning: old installation of Sequitur found. You should manually"
  echo  >&2 "  delete the directories tools/sequitur and/or tools/g2p and "
  echo  >&2 "  edit the file tools/env.sh and remove manually all references to it"
  exit 1
fi

if [ ! -d ./sequitur-g2p ] ; then
  $GIT clone https://github.com/sequitur-g2p/sequitur-g2p.git sequitur-g2p
fi
```

```shell
(
cd sequitur-g2p

# Apple을 고려하는 부분 삭제
make CXX=g++ CC=gcc



# PATHONPATH 변수 설정에서의 문제가 발생하여 해당 부분 코드 수정
site_packages_dir=$(PYTHONPATH="" python -m site --user-site | grep -oE "lib.*")
SEQUITUR=$(pwd)/$site_packages_dir
# some bits of info to troubleshoot this in case people have problems
echo -n  >&2 "USER SITE: "; PYTHONPATH="" python -m site --user-site
echo >&2 "SEQUITUR_PACKAGE: ${site_packages_dir:-}"
echo >&2 "SEQUITUR: $SEQUITUR"
echo >&2 "PYTHONPATH: ${PYTHONPATH:-}"
mkdir -p $SEQUITUR
PYTHONPATH=$SEQUITUR
PYTHONUSERBASE=$(pwd)
python setup.py install --user --prefix=
) || {
  echo >&2 "Problem installing sequitur!"
  exit 1
}

site_packages_dir=$(cd sequitur-g2p; find ./lib -type d -name site-packages | head -n 1)
(
  set +u
  [ ! -z "${SEQUITUR}" ] && \
    echo >&2 "SEQUITUR variable is aleady defined. Undefining..." && \
    unset SEQUITUR

  [ -f ./env.sh ] && . ./env.sh

  [ ! -z "${SEQUITUR}" ] && \
    echo >&2 "SEQUITUR config is already in env.sh" && exit

  wd=`pwd`
  wd=`readlink -f $wd || pwd`

  echo "export SEQUITUR=\"$wd/sequitur-g2p\""
  echo "export PATH=\"\$PATH:\${SEQUITUR}/bin\""
  echo "export PYTHONPATH=\"\${PYTHONPATH:-}:\$SEQUITUR/${site_packages_dir}\""
) >> env.sh

echo >&2 "Installation of SEQUITUR finished successfully"
echo >&2 "Please source tools/env.sh in your path.sh to enable it"

```

> 마지막에 source env.sh 실행필요