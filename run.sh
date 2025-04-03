#!/bin/bash

set -e

echo "=== [1] 운영체제 감지 중... ==="
OS="$(uname -s)"
DISTRO=""

echo "Detected OS: $OS"

if [ "$OS" == "Linux" ]; then
    if grep -qi microsoft /proc/version; then
        echo "Running under WSL (Ubuntu assumed)..."
        DISTRO="ubuntu"
    elif [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    fi

    if [[ "$DISTRO" == "ubuntu" || "$DISTRO" == "debian" ]]; then
        echo "Setting up for Ubuntu/Debian..."
        sudo apt update
        sudo apt-get install -y ffmpeg build-essential
        sudo apt-get install -y portaudio19-dev libasound-dev
        sudo apt-get install -y libxcb-xinerama0 libxcb1 libxcb-util1 libx11-xcb1 libxrender1 libxi6 libxext6
        sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-4.0
        sudo apt-get install -y libgirepository-2.0-dev gcc libcairo2-dev pkg-config python3-dev python3-venv
        sudo apt-get install fonts-nanum

    elif [[ "$DISTRO" == "arch" || "$DISTRO" == "manjaro" ]]; then
        echo "Setting up for Arch/Manjaro..."
        sudo pacman -Syu --noconfirm
        sudo pacman -S --noconfirm ffmpeg base-devel portaudio libasound
        sudo pacman -S --noconfirm cairo pkgconf python-gobject gtk4 python-virtualenv

    elif [[ "$DISTRO" == "centos" || "$DISTRO" == "rhel" ]]; then
        echo "Setting up for CentOS/RHEL..."
        sudo yum install -y epel-release
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y ffmpeg gcc-c++ make portaudio-devel alsa-lib-devel cairo-devel pkgconfig python3-devel python3-venv gobject-introspection-devel gtk4

    else
        echo "Unsupported Linux distro: $DISTRO"
        exit 1
    fi

elif [ "$OS" == "Darwin" ]; then
    echo "Setting up for macOS..."
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install ffmpeg portaudio cairo pkg-config python gobject-introspection gtk4

else
    echo "Unsupported OS: $OS"
    exit 1
fi

echo "=== [2] 가상환경 생성 중... ==="

if [ ! -d "./dolbom_venv" ]; then
    python3 -m venv dolbom_venv
    echo "가상환경 'dolbom_venv' 생성 완료"
else
    echo "가상환경 'dolbom_venv' 이미 존재함"
fi

source dolbom_venv/bin/activate

echo "=== 더 이상 사용되지 않는 이전 버전의 패키지 제거 중... ==="
pip uninstall -y gpt4all

echo "=== [3] 기존 충돌 패키지 제거 중... ==="
pip uninstall -y PyQt5 opencv-python-headless opencv-python

echo "=== [4] Python 패키지 설치 중... ==="
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "모든 설치가 완료되었습니다!"
echo ""
echo "  ▶ 가상환경 재진입:        source dolbom_venv/bin/activate"
echo "  ▶ 가상환경 종료:          deactivate"
echo ""
echo "  ▶ 기본 실행:              python3 main.py"
echo "  ▶ GUI 실행:              python3 main.py      # '-g' 없이도 실행됩니다"
echo "  ▶ GUI 종료 방법:         창 닫기 또는 Ctrl + C"
echo "  ▶ GUI 강제 중지:         python3 main.py --stop"
echo ""

read -p "▶ 설치가 완료되었습니다. 지금 바로 실행할까요? (y/N): " run_now

if [[ "$run_now" == "y" || "$run_now" == "Y" || "$run_now" == "yes" || "$run_now" == "네" || "$run_now" == "ㅇ" || "$run_now" == "ㅇㅇ" ]]; then
    echo ""
    echo "main.py 실행 중..."
    python3 main.py
else
    echo "실행을 건너뜁니다. 필요 시 다음 명령을 입력하세요:"
    echo "   source dolbom_venv/bin/activate"
    echo "   python3 main.py"
fi
