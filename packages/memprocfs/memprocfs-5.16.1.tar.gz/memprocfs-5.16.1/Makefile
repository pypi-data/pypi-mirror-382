
all:
	$(MAKE) -C leechcore
	$(MAKE) -C vmm || true
	cp files/vmm.so .
	cp files/*.so memprocfs/

clean:
	$(MAKE) clean -C leechcore
	$(MAKE) clean -C vmm
	rm files/*.so || true
	rm vmm.so || true
	rm memprocfs/*.so || true

