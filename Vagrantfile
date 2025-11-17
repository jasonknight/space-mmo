# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu64/noble64"
  config.vm.hostname = "gdb"
  config.vm.network "private_network", ip: "10.0.0.100"
  
  config.vm.box_check_update = false
  config.vm.provider "virtualbox" do |v|
    v.name = "gamedb"
    v.memory = 1024 * 8
    v.cpus = 4
  end
end
