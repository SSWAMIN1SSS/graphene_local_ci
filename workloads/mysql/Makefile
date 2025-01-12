ARCH_LIBDIR ?= /lib/$(shell $(CC) -dumpmachine)
UID ?= $(shell id -u)
GID ?= $(shell id -g)

ifeq ($(DEBUG),1)
GRAMINE_LOG_LEVEL = debug
else
GRAMINE_LOG_LEVEL = error
endif

.PHONY: all
all: mysqld.manifest
ifeq ($(SGX),1)
all: mysqld.manifest.sgx mysqld.sig
endif

mysqld.manifest: mysqld.manifest.template
	gramine-manifest \
	-Dlog_level=$(GRAMINE_LOG_LEVEL) \
	-Darch_libdir=$(ARCH_LIBDIR) \
	-Duid=$(UID) \
	-Dgid=$(GID) \
	-Dentrypoint=$(realpath $(shell sh -c "command -v mysqld")) \
	$< >$@

# Make on Ubuntu <= 20.04 doesn't support "Rules with Grouped Targets" (`&:`),
# for details on this workaround see
# https://github.com/gramineproject/gramine/blob/e8735ea06c/CI-Examples/helloworld/Makefile
mysqld.manifest.sgx mysqld.sig: sgx_sign
	@:

.INTERMEDIATE: sgx_sign
sgx_sign: mysqld.manifest
	gramine-sgx-sign \
	--manifest $< \
	--output $<.sgx


ifeq ($(SGX),)
GRAMINE = gramine-direct
else
GRAMINE = gramine-sgx
endif

.PHONY: check
check: all
	mysqld --initialize-insecure --datadir=/tmp/mysql-data 2>&1 | tee OUTPUT
	@grep -q '\[Server\] root@localhost is created with an empty password !' OUTPUT && echo [ "Success 1/2" ]
	sleep 5s && $(GRAMINE) mysqld --datadir /tmp/mysql-data &

#.PHONY: run-native
#run-native: all
#	mysqld --initialize-insecure --datadir=/tmp/mysql-data 2>&1 | tee OUTPUT
#	@grep -q '\[Server\] root@localhost is created with an empty password !' OUTPUT && echo [ "Success 1/2" ]
#	sleep 5s && mysqld --datadir /tmp/mysql-data &

.PHONY: install-dependencies
install-dependencies:
	#apt update
	-pkill -9 mysqld
	apt install -y mysql-server
	apt install -y sysbench
	sed -i "s|^\(log_error.*\)|#\1|g" /etc/mysql/mysql.conf.d/mysqld.cnf
	systemctl stop mysql.service
	mkdir -p /var/run/mysqld
	mkdir -p /var/lib/mysql-files
	chown -R mysql:mysql /var/run/mysqld
	chown -R mysql:mysql /var/lib/mysql-files

#.PHONY: privileges
#privileges:
#	sudo chown -R $$USER:$$USER /var/run/mysqld
#	sudo chown -R $$USER:$$USER /var/lib/mysql-files

.PHONY: uninstall-mysql
uninstall-mysql:
	-pkill -9 mysqld
	apt remove --purge -y mysql-server sysbench
	apt autoremove --purge -y
	rm -rf /var/run/mysqld /tmp/mysql-data /var/lib/mysql-files *.sig *.manifest.sgx *.manifest

.PHONY: conncheck
conncheck:
	sleep 55s && sudo mysqladmin -h 127.0.0.1 -P 3306 create sbtest
	sysbench --db-driver=mysql --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-db=sbtest --time=20 --report-interval=5 oltp_read_write --tables=2 --table_size=100000 --threads=32 prepare 2>&1 | tee CREATE_RESULT
	sysbench --db-driver=mysql --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-db=sbtest --time=20 --report-interval=5 oltp_read_write --tables=2 --table_size=100000 --threads=32 run 2>&1 | tee RUN_RESULT
	sysbench --db-driver=mysql --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-db=sbtest --time=20 --report-interval=5 oltp_read_write --tables=2 --table_size=100000 --threads=32 cleanup 2>&1 | tee DELETE_RESULT
	#sudo mysqladmin -h 127.0.0.1 -P 3306 drop sbtest

.PHONY: clean
clean:
	$(RM) *.sig *.manifest.sgx *.manifest
	$(RM) -r /tmp/mysql-data

.PHONY: distclean
distclean: clean
