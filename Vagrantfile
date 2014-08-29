# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "trusty64"
  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"
  config.vm.network :forwarded_port, guest: 80, host: 8080
  config.vm.network :forwarded_port, guest: 22, host: 6174
  config.vm.network :forwarded_port, guest: 8000, host: 8000
  config.vm.network :forwarded_port, guest: 27017, host: 27017
  config.vm.network :forwarded_port, guest: 1337, host: 1337
  config.vm.synced_folder "api", "/home/vagrant/api"
  config.vm.synced_folder "web", "/home/vagrant/web"
  config.vm.synced_folder "scripts", "/home/vagrant/scripts"
  config.vm.synced_folder "minigames", "/home/vagrant/minigames"
  config.vm.synced_folder "game", "/home/vagrant/game"
  config.vm.synced_folder "webex", "/home/vagrant/webex"
  config.vm.provision :shell, :path => "scripts/vagrant_setup.sh"
  config.ssh.forward_agent = true

  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--memory", "2048"]
  end
end

