# -*- mode: ruby -*-
# vi: set ft=ruby :

ISO_PATH = File.expand_path("~/ISO-images/metal-amd64.iso")
STORAGE_POOL = "pool-talos"
CONTROL_PLANES_COUNT = 1
WORKERS_COUNT = 2

Vagrant.configure("2") do |config|
  config.vm.synced_folder ".", "/vagrant", disabled: true

  # Control Plane узлы (мастер)
  (1..CONTROL_PLANES_COUNT).each do |i|
    vm_name = "talos-cp-#{i}"
    config.vm.define vm_name do |node|
      node.vm.provider :libvirt do |lv|
        lv.memory = 2048
        lv.cpus = 2
        lv.storage :file, :device => :cdrom, :path => ISO_PATH
        lv.storage_pool_name = STORAGE_POOL
        # Имя диска = имя VM + .qcow2
        lv.storage :file, :size => '10G', :name => "#{vm_name}.qcow2"
        lv.boot 'hd'
        lv.boot 'cdrom'
      end
    end
  end

  # Worker узлы
  (1..WORKERS_COUNT).each do |i|
    vm_name = "talos-worker-#{i}"
    config.vm.define vm_name do |node|
      node.vm.provider :libvirt do |lv|
        lv.memory = 4096
        lv.cpus = 2
        lv.storage :file, :device => :cdrom, :path => ISO_PATH
        lv.storage_pool_name = STORAGE_POOL
        lv.storage :file, :size => '10G', :name => "#{vm_name}.qcow2"
        lv.boot 'hd'
        lv.boot 'cdrom'
      end
    end
  end
end