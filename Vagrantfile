# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "trusty64"
  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"
  config.vm.network :forwarded_port, guest: 80, host: 8080
  config.vm.network :forwarded_port, guest: 22, host: 6174
  #config.vm.synced_folder "deploy", "/deploy"
  config.vm.synced_folder "api", "/home/vagrant/api"
  config.vm.provision :shell, :path => "scripts/vagrant_setup.sh"
  config.ssh.forward_agent = true
end
