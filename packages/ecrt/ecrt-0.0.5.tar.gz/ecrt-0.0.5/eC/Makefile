ifneq ($(V),1)
.SILENT:
endif

.PHONY: all bootstrap cleantarget clean realclean wipeclean distclean ecrt ectp ecp ecc ecs ecrt_static ectp_static outputdirs bindings clean_python_bindings c_bindings cpp_bindings py_bindings rust_bindings install

CONFIG := release

_CF_DIR = ./

include $(_CF_DIR)crossplatform.mk
include $(_CF_DIR)default.cf

.NOTPARALLEL: $(NOT_PARALLEL_TARGETS)

XBOOT := $(if $(CROSS_TARGET),GCC_PREFIX= TARGET_PLATFORM=$(HOST_PLATFORM) PLATFORM=$(HOST_PLATFORM),)

LIBVER := .0.0.5

ifdef WINDOWS_HOST
HOST_SOV := $(HOST_SO)
else
HOST_SOV := $(HOST_SO)$(LIBVER)
endif

ifdef WINDOWS_HOST
PYTHON := python
else
PYTHON := python3
endif

ifdef WINDOWS_TARGET

SOV := $(SO)

ifndef DESTDIR

ifndef ECERE_SDK_INSTALL_DIR

ifeq ($(TARGET_ARCH),x86_64)
   ifneq ($(wildcard $(SystemDrive)/Program\ Files ),)
      export DESTDIR=$(SystemDrive)/Program Files/Ecere SDK
   else
      export DESTDIR=$(SystemDrive)/Ecere SDK
   endif
else
   ifdef ProgramFiles(x86)
      export DESTDIR=${ProgramFiles(x86)}/Ecere SDK
   else
      ifdef ProgramFiles
         export DESTDIR=$(ProgramFiles)/Ecere SDK
      else
         export DESTDIR=$(SystemDrive)/Ecere SDK
      endif
   endif
endif

else
	export DESTDIR=$(ECERE_SDK_INSTALL_DIR)
endif # ECERE_SDK_INSTALL_DIR

endif # DESTDIR

export prefix=

ifndef DOCDIR
export DOCDIR=$(DESTDIR)$(prefix)/doc
endif

ifndef BINDIR
export BINDIR=$(DESTDIR)$(prefix)/bin
endif

ifndef LIBDIR
export LIBDIR=$(BINDIR)
endif
export DESTLIBDIR=$(LIBDIR)

ifndef SLIBDIR
export SLIBDIR=$(DESTDIR)$(prefix)/lib
endif
export DESTSLIBDIR=$(SLIBDIR)

ifndef SAMPLESDIR
export SAMPLESDIR=$(DESTDIR)$(prefix)/samples
endif

ifndef EXTRASDIR
export EXTRASDIR=$(DESTDIR)$(prefix)/extras
endif


else # WINDOWS_TARGET

ifdef OSX_TARGET
# TODO: OSX soname
SOV := $(SO)
else
ifndef SKIP_SONAME
SOV := $(SO)$(LIBVER)
else
SOV := $(SO)
endif
endif

ifndef DESTDIR
export DESTDIR=
endif

ifndef prefix
export prefix=/usr
endif

ifndef DOCDIR
export DOCDIR=$(DESTDIR)$(prefix)/share/ecere/doc
endif

ifndef MANDIR
export MANDIR=$(DESTDIR)$(prefix)/share/man
endif

ifndef BINDIR
export BINDIR=$(DESTDIR)$(prefix)/bin
endif

ifdef LIBDIR
 export PREFIXLIBDIR=$(LIBDIR)
else
 export PREFIXLIBDIR=$(prefix)/lib/$(TARGET_ARCH)

 ifeq ($(wildcard $(prefix)/lib/$(TARGET_ARCH)),)
  export PREFIXLIBDIR=$(prefix)/lib$(LIB32_SFX)

  ifeq ($(TARGET_TRIPLE),i386-linux-gnu)
   ifneq ($(wildcard $(prefix)/lib32),)
    export PREFIXLIBDIR=$(prefix)/lib32
   endif
  endif

 endif
endif

export CPPFLAGS
CPPFLAGS += -DDEB_HOST_MULTIARCH=\"$(call escspace,$(PREFIXLIBDIR))\"

DESTLIBDIR := $(DESTDIR)$(PREFIXLIBDIR)
ifdef SLIBDIR
DESTSLIBDIR := $(DESTDIR)$(SLIBDIR)
else
DESTSLIBDIR := $(DESTLIBDIR)
endif

ifndef SAMPLESDIR
export SAMPLESDIR=$(DESTDIR)$(prefix)/share/ecere/samples
endif

ifndef EXTRASDIR
export EXTRASDIR=$(DESTDIR)$(prefix)/share/ecere/extras
endif


endif


OBJDIR := obj$(OBJALT)/
OBJBINDIR := $(OBJDIR)$(PLATFORM)$(COMPILER_SUFFIX)$(DEBUG_SUFFIX)/bin/
OBJLIBDIR := $(OBJDIR)$(PLATFORM)$(COMPILER_SUFFIX)$(DEBUG_SUFFIX)/lib/
XOBJDIR := obj$(OBJALT)/
XOBJBINDIR := $(OBJDIR)$(HOST_PLATFORM)$(COMPILER_SUFFIX)$(DEBUG_SUFFIX)/bin/
XOBJLIBDIR := $(OBJDIR)$(HOST_PLATFORM)$(COMPILER_SUFFIX)$(DEBUG_SUFFIX)/lib/

all: ecp ecc ecs ecrt_static ear #epj2make ectp_static

outputdirs:
	$(call mkdir,$(OBJDIR))
	$(call mkdir,$(OBJBINDIR))
	$(call mkdir,$(OBJLIBDIR))
ifdef CROSS_TARGET
	$(call mkdir,$(XOBJDIR))
	$(call mkdir,$(XOBJBINDIR))
	$(call mkdir,$(XOBJLIBDIR))
endif

ecrt: bootstrap outputdirs
ifdef CROSS_TARGET
	@$(call echo,Building 2nd stage eC runtime library (host)...)
else
	@$(call echo,Building 2nd stage eC runtime library...)
endif
# TOCHECK: $(XBOOT) Even when not using cross-target?
	+cd ecrt && $(_MAKE) nores $(XBOOT)
	+cd ear && $(_MAKE) nores $(XBOOT)
	+cd ecrt && $(_MAKE) cleanecrttarget
ifdef CROSS_TARGET
	@$(call echo,Building 2nd stage eC runtime library...)
endif
	+cd ecrt && $(_MAKE)

ecrt_static: ecc ecs ecp
	@$(call echo,Building static eC runtime library...)
	+cd ecrt && $(_MAKE) -f Makefile.static

ectp: ecrt
ifdef CROSS_TARGET
	@$(call echo,Building 2nd stage eC transpiler library (host))
	+cd ectp && $(_MAKE) $(XBOOT)
endif
	@$(call echo,Building 2nd stage eC transpiler library...)
	+cd ectp && $(_MAKE)

ectp_static: ecc ecs ecp
	@$(call echo,Building static eC transpiler library...)
	+cd ectp && $(_MAKE) -f Makefile.static

ecp: ectp
	@$(call echo,Building 2nd stage eC precompiler...)
	+cd ecp && $(_MAKE)

ecc: ectp
	@$(call echo,Building 2nd stage eC compiler...)
	+cd ecc && $(_MAKE)

ecs: ectp
	@$(call echo,Building 2nd stage eC symbol generator...)
	+cd ecs && $(_MAKE)

ear: ecrt ecrt_static
	@$(call echo,Building ear...)
	+cd ear && $(_MAKE) cleantarget
	+cd ear && $(_MAKE)

#epj2make: ecrt ear
#	@$(call echo,Building epj2make...)
#	+cd epj2make && $(_MAKE)

bootstrap:
	@$(call echo,Bootstrapping eC compiling tools...)
	+cd bootstrap && $(_MAKE) $(XBOOT)

regenbootstrap: update_ecrt update_ectp update_ecp update_ecc update_ecs
	@echo Bootstrap regenerated.

updatebootstrap: regenbootstrap
	@echo Copying files...
	$(call cp,ecrt/obj/bootstrap.$(PLATFORM)$(COMPILER_SUFFIX)$(DEBUG_SUFFIX)/*.c,bootstrap/ecrt/bootstrap)
	$(call cp,ectp/obj/bootstrap.$(PLATFORM)$(COMPILER_SUFFIX)$(DEBUG_SUFFIX)/*.c,bootstrap/ectp/bootstrap)
	$(call cp,ecp/obj/bootstrap.$(PLATFORM)$(COMPILER_SUFFIX)$(DEBUG_SUFFIX)/*.c,bootstrap/ecp/bootstrap)
	$(call cp,ecc/obj/bootstrap.$(PLATFORM)$(COMPILER_SUFFIX)$(DEBUG_SUFFIX)/*.c,bootstrap/ecc/bootstrap)
	$(call cp,ecs/obj/bootstrap.$(PLATFORM)$(COMPILER_SUFFIX)$(DEBUG_SUFFIX)/*.c,bootstrap/ecs/bootstrap)
	@echo Bootstrap updated.

update_ecrt:
	@echo Regenerating ecrt bootstrapper...
	+cd ecrt && $(_MAKE) -f Makefile.bootstrap clean
	+cd ecrt && $(_MAKE) -f Makefile.bootstrap

update_ectp:
	@echo Regenerating ectp bootstrapper...
	+cd ectp && $(_MAKE) -f Makefile.bootstrap clean
	+cd ectp && $(_MAKE) -f Makefile.bootstrap

update_ecp:
	@echo Regenerating ecp bootstrapper...
	+cd ecp && $(_MAKE) -f Makefile.bootstrap clean
	+cd ecp && $(_MAKE) -f Makefile.bootstrap

update_ecc:
	@echo Regenerating ecc bootstrapper...
	+cd ecc && $(_MAKE) -f Makefile.bootstrap clean
	+cd ecc && $(_MAKE) -f Makefile.bootstrap

update_ecs:
	@echo Regenerating ecs bootstrapper...
	+cd ecs && $(_MAKE) -f Makefile.bootstrap clean
	+cd ecs && $(_MAKE) -f Makefile.bootstrap

c_bindings:
	@echo Building C bindings...
	+cd bindings/c && $(MAKE)

cpp_bindings: c_bindings
	@echo Building C++ bindings...
	+cd bindings/cpp && $(MAKE)

py_bindings: c_bindings
	@echo Building Python bindings...
	+cd bindings/py && $(PYTHON) build_ecrt.py

rust_bindings: c_bindings
	@echo Building Rust bindings...
	+cd bindings/rust && $(MAKE)

bindings: c_bindings cpp_bindings py_bindings rust_bindings

cleantarget:
	+cd bootstrap && $(_MAKE) cleantarget
	+cd ecrt && $(_MAKE) cleantarget
	+cd ectp && $(_MAKE) cleantarget
	+cd ecp && $(_MAKE) cleantarget
	+cd ecc && $(_MAKE) cleantarget
	+cd ecs && $(_MAKE) cleantarget
	+cd ear && $(_MAKE) cleantarget
#	+cd epj2make && $(_MAKE) cleantarget

clean_python_bindings:
	+cd bindings/py && rm -rf *.c *.o *.so *.dyld *.dll __pycache__ projects

clean: clean_python_bindings
	+cd bootstrap && $(_MAKE) clean
	+cd ecrt && $(_MAKE) clean
	+cd ectp && $(_MAKE) clean
	+cd ecp && $(_MAKE) clean
	+cd ecc && $(_MAKE) clean
	+cd ecs && $(_MAKE) clean
	+cd ear && $(_MAKE) clean
#	+cd epj2make && $(_MAKE) clean
	+cd bindings/c && $(MAKE) clean
	+cd bindings/cpp && $(MAKE) clean
	+cd bindings/rust && $(MAKE) clean

realclean: clean_python_bindings
	+cd bootstrap && $(_MAKE) realclean
	+cd ecrt && $(_MAKE) realclean
	+cd ectp && $(_MAKE) realclean
	+cd ecp && $(_MAKE) realclean
	+cd ecc && $(_MAKE) realclean
	+cd ecs && $(_MAKE) realclean
	+cd ear && $(_MAKE) realclean
#	+cd epj2make && $(_MAKE) realclean
	+cd bindings/c && $(MAKE) realclean
	+cd bindings/cpp && $(MAKE) realclean
	+cd bindings/rust && $(MAKE) realclean

wipeclean: clean_python_bindings
	+cd bootstrap && $(_MAKE) wipeclean
	+cd ecrt && $(_MAKE) wipeclean
	+cd ectp && $(_MAKE) wipeclean
	+cd ecp && $(_MAKE) wipeclean
	+cd ecc && $(_MAKE) wipeclean
	+cd ecs && $(_MAKE) wipeclean
	+cd ear && $(_MAKE) wipeclean
#	+cd epj2make && $(_MAKE) wipeclean
	+cd bindings/c && $(MAKE) wipeclean
	+cd bindings/cpp && $(MAKE) wipeclean
	+cd bindings/rust && $(MAKE) wipeclean

distclean:
	$(_MAKE) -f $(_CF_DIR)Cleanfile distclean distclean_all_subdirs

install:
ifdef WINDOWS_TARGET
	$(call mkdir,$(call path,$(BINDIR)/))
	$(call mkdir,$(call path,$(DESTSLIBDIR)/))
	$(call cp,$(OBJBINDIR)$(LP)ecrt$(SO),"$(DESTLIBDIR)/")
	$(call cp,$(OBJBINDIR)$(LP)ectp$(SO),"$(DESTLIBDIR)/")
	$(call cp,$(OBJBINDIR)ear$(B32_SFX)$(E),"$(BINDIR)/")
	$(call cp,$(OBJBINDIR)ecc$(B32_SFX)$(E),"$(BINDIR)/")
	$(call cp,$(OBJBINDIR)ecp$(B32_SFX)$(E),"$(BINDIR)/")
	$(call cp,$(OBJBINDIR)ecs$(B32_SFX)$(E),"$(BINDIR)/")
#	$(call cp,$(OBJBINDIR)epj2make$(E),"$(BINDIR)/")
	$(call cp,$(OBJLIBDIR)libecrtStatic$(A),"$(DESTSLIBDIR)/")
endif

ifdef OSX_TARGET
	install $(OBJLIBDIR)$(LP)ecrt$(SO) $(DESTLIBDIR)/
	install $(OBJLIBDIR)$(LP)ectp$(SO) $(DESTLIBDIR)/
	install $(OBJBINDIR)ear$(B32_SFX)$(E) $(BINDIR)/
	install $(OBJBINDIR)ecc$(B32_SFX)$(E) $(BINDIR)/
	install $(OBJBINDIR)ecp$(B32_SFX)$(E) $(BINDIR)/
	install $(OBJBINDIR)ecs$(B32_SFX)$(E) $(BINDIR)/
#	install $(OBJBINDIR)epj2make$(E) $(BINDIR)/
	install $(OBJLIBDIR)libecrtStatic$(A) $(DESTSLIBDIR)/
	mkdir -p $(MANDIR)/man1
	cp -pRf share/man/man1/* $(MANDIR)/man1
endif

ifndef OSX_TARGET
ifndef WINDOWS_TARGET
ifdef LINUX_TARGET
	mkdir -p $(DESTLIBDIR)/ec
	mkdir -p $(BINDIR)/
	install $(INSTALL_FLAGS) $(OBJLIBDIR)$(LP)ecrt$(SOV) $(DESTLIBDIR)/$(LP)ecrt$(SOV)
	install $(INSTALL_FLAGS) $(OBJLIBDIR)$(LP)ectp$(SOV) $(DESTLIBDIR)/ec/$(LP)ectp$(SOV)
ifndef SKIP_SONAME
	ln -sf $(LP)ecrt$(SOV) $(DESTLIBDIR)/$(LP)ecrt$(SO).0
	ln -sf $(LP)ectp$(SOV) $(DESTLIBDIR)/ec/$(LP)ectp$(SO).0
	ln -sf $(LP)ecrt$(SOV) $(DESTLIBDIR)/$(LP)ecrt$(SO)
	ln -sf $(LP)ectp$(SOV) $(DESTLIBDIR)/ec/$(LP)ectp$(SO)
	ln -sf ../$(LP)ecrt$(SOV) $(DESTLIBDIR)/ec/$(LP)ecrt$(SO)
endif
else
	install $(INSTALL_FLAGS) $(OBJLIBDIR)$(LP)ecrt$(SO) $(DESTLIBDIR)/$(LP)ecrt$(SO)
endif
	install $(INSTALL_FLAGS) $(OBJBINDIR)ear$(B32_SFX)$(E) $(BINDIR)/ear$(B32_SFX)$(E)
	install $(INSTALL_FLAGS) $(OBJBINDIR)ecc$(B32_SFX)$(E) $(BINDIR)/ecc$(B32_SFX)$(E)
	install $(INSTALL_FLAGS) $(OBJBINDIR)ecp$(B32_SFX)$(E) $(BINDIR)/ecp$(B32_SFX)$(E)
	install $(INSTALL_FLAGS) $(OBJBINDIR)ecs$(B32_SFX)$(E) $(BINDIR)/ecs$(B32_SFX)$(E)
#	install $(INSTALL_FLAGS) $(OBJBINDIR)epj2make$(E) $(BINDIR)/epj2make$(E)
	install $(INSTALL_FLAGS) $(OBJLIBDIR)libecrtStatic$(A) $(DESTSLIBDIR)/libecrtStatic$(A)
	mkdir -p $(MANDIR)/man1
	cp -pRf share/man/man1/* $(MANDIR)/man1
endif
endif
	@$(call echo,The eC SDK$(if $(CROSS_BIT32), (32-bit),) has been installed.)

$(MAKEFILE_LIST): ;
$(SOURCES): ;
$(RESOURCES): ;
