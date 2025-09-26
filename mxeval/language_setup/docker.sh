#!/bin/bash

# Set non-interactive mode for apt
export DEBIAN_FRONTEND=noninteractive

printf "%100s" " " | tr ' ' '-'
echo ""
echo "setting up Ruby "
printf "%100s" " " | tr ' ' '-'
echo ""
apt-get update
apt-get install -y git curl libssl-dev libreadline-dev zlib1g-dev autoconf bison build-essential libyaml-dev libncurses5-dev libffi-dev libgdbm-dev

# Install Ruby via rbenv
curl -fsSL https://github.com/rbenv/rbenv-installer/raw/HEAD/bin/rbenv-installer | bash
export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"
rbenv install 3.0.0
rbenv global 3.0.0

printf "%100s" " " | tr ' ' '-'
echo ""
echo "setting up php "
printf "%100s" " " | tr ' ' '-'
echo ""
apt-get install -y software-properties-common ca-certificates lsb-release apt-transport-https
# Use non-interactive add-apt-repository
add-apt-repository -y ppa:ondrej/php
apt-get update
apt-get install -y php8.0
apt-get install -y php-{pear,cgi,pdo,common,curl,mbstring,gd,mysqlnd,gettext,bcmath,json,xml,fpm,intl,zip}

printf "%100s" " " | tr ' ' '-'
echo ""
echo "setting up Java "
printf "%100s" " " | tr ' ' '-'
echo ""
apt-get install -y openjdk-8-jdk

printf "%100s" " " | tr ' ' '-'
echo ""
echo "setting up JavaScript "
printf "%100s" " " | tr ' ' '-'
echo ""
apt-get install -y curl nodejs npm
# Install specific Node.js version if needed
npm install -g n
n 16.10.0
npm install -g lodash

printf "%100s" " " | tr ' ' '-'
echo ""
echo "setting up TypeScript "
printf "%100s" " " | tr ' ' '-'
echo ""
npm install -g typescript

printf "%100s" " " | tr ' ' '-'
echo ""
echo "setting up Go "
printf "%100s" " " | tr ' ' '-'
echo ""
# Install Go
cd /usr/local
wget https://go.dev/dl/go1.19.1.linux-amd64.tar.gz
tar -xzf go1.19.1.linux-amd64.tar.gz
rm go1.19.1.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

printf "%100s" " " | tr ' ' '-'
echo ""
echo "setting up Swift "
printf "%100s" " " | tr ' ' '-'
echo ""
cd /usr/local
swift_release="swift-5.7-RELEASE-ubuntu20.04.tar.gz"
wget "https://download.swift.org/swift-5.7-release/ubuntu2004/swift-5.7-RELEASE/$swift_release"
tar -xzf $swift_release
rm $swift_release
export PATH="${PATH}:/usr/local/swift-5.7-RELEASE-ubuntu20.04/usr/bin"

printf "%100s" " " | tr ' ' '-'
echo ""
echo "setting up Scala "
printf "%100s" " " | tr ' ' '-'
echo ""
apt-get install -y scala

printf "%100s" " " | tr ' ' '-'
echo ""
echo "setting up C# "
printf "%100s" " " | tr ' ' '-'
echo ""
apt-get update
apt-get install -y dotnet6

printf "%100s" " " | tr ' ' '-'
echo ""
echo "setting up Perl "
printf "%100s" " " | tr ' ' '-'
echo ""
# Install Perl modules non-interactively
cpan -T Data::Compare

printf "%100s" " " | tr ' ' '-'
echo ""
echo "setting up Kotlin "
printf "%100s" " " | tr ' ' '-'
echo ""
apt-get install -y zip unzip
curl -s https://get.sdkman.io | bash
export SDKMAN_DIR="$HOME/.sdkman"
source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk install kotlin

# Set up final PATH for all languages
export PATH="${PATH}:/usr/local/swift-5.7-RELEASE-ubuntu20.04/usr/bin:/usr/local/go/bin"

printf "%100s" " " | tr ' ' '-'
echo ""
echo 'Installation complete.'
printf "%100s" " " | tr ' ' '-'
echo ""
