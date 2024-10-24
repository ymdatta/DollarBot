#!/bin/bash
if ! type pyenv > /dev/null 2>&1; then
    echo "pyenv not installed. Installing pyenv..."
    rm -rf ~/.pyenv
    curl https://pyenv.run | bash
    echo '' >> $HOME/.bashrc
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> $HOME/.bashrc
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> $HOME/.bashrc
    echo 'eval "$(pyenv init --path)"' >> $HOME/.bashrc
    echo 'eval "$(pyenv init -)"' >> $HOME/.bashrc
    echo 'eval "$(pyenv virtualenv-init -)"' >> $HOME/.bashrc
    source $HOME/.bashrc
    pyenv --version
    echo "Pyenv installed. Environment updated."
else
    echo "pyenv is already installed."
fi
