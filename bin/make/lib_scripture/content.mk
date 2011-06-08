# content.mk

# This file provides build rules for building all scripture material
# in a typical Scripture publication

# History:

# 20110608 - djd - Initial version created from ptxplus


##############################################################
#		Rules for publication Scripture content
##############################################################

# Before we can typeset we have to copy the source text
# into the Source folder. After that further preprocessing
# is needed. Any predictable process will be done here.
# The list of processes can be edited in the project ini
# ini under the [Preproces] section.

# Define the main macro for what it takes to process an
# individual component.

define content_rules

# Define our source file rule here. The idea is we do not want the
# user to get a file not found error when they process a file.
# Rather a dummy file will be created telling them the file is missing
# and hopefully some helpful instructions on what to do.
$(PATH_SOURCE)/$($(1)_content)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE) :
	$(call copysmart,$(PATH_RESOURCES_TEMPLATES)/$($(1)_content)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE),$$@)

# This is the rule for creating the working text. We will use
# the postprocessing function to do this.
$(PATH_TEXTS)/$(1).$(EXT_WORK) : $(PATH_SOURCE)/$($(1)_content)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE)
ifeq ($(LOCKED),0)
	@echo INFO: Creating: $(PATH_TEXTS)/$(1).$(EXT_WORK)
	$$(call postprocessing,$(1),$($(1)_content))
else
	@echo INFO: Cannot create: $$@ because the project is locked.
endif

# This enables us to do the preprocessing on a single component and view the log file
# We will not do individual checks here as there can be a good number of them.
# If we implement that it will be in a different control file to simplify things.
# If we are checking text that means we are not sure about how good it is. That
# being the case, we don't want this text in the system yet so the very first
# thing we do is try to delete any existing copies from the source directory.
preprocess-$(1) : $(PATH_SOURCE)/$($(1)_content)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE) $(DEPENDENT_FILE_LIST)
ifeq ($(LOCKED),0)
	$$(call preprocessing,$(1),$($(1)_content))
else
	@echo INFO: Cannot process: $$@ because the project is locked.
endif

# Call a postprocessing function which will run all the postprocesses.
# When the post processing is done we will run a benchmark test to
# account for any changes made.
postprocess-$(1) : $(PATH_SOURCE)/$($(1)_content)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE) $(DEPENDENT_FILE_LIST)
ifeq ($(LOCKED),0)
	$$(call postprocessing,$(1),$($(1)_content))
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "$(1)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" "" ""
else
	@echo INFO: Cannot post process: $(PATH_TEXTS)/$(1).$(EXT_WORK) because the project is locked.
endif

# Call the TeX control file creation script to create a simple
# control file that will link to the other settings
$(PATH_PROCESS)/$(1).$(EXT_TEX) : $(PATH_PROCESS)/$(FILE_TEX_SETTINGS)
ifeq ($(LOCKED),0)
	@echo INFO: Creating: $$@
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEX)" "$(1)" "$(1).$(EXT_WORK)" "$$@" ""
else
	@echo INFO: Cannot create: $$@ This is because the project is locked.
endif

# Process a single component and produce the final PDF. A Special
# dependency is set for the .adj file in case it has been altered.
# An even more special dependency is set on the piclist file and
# hyphenation file too with an [if] statement because not every
# component has to have a piclist or hypheation.
$(PATH_PROCESS)/$(1).$(EXT_PDF) : \
		$(PATH_TEXTS)/$(1).$(EXT_WORK) \
		$(PATH_PROCESS)/$(1).$(EXT_TEX) \
		$(PATH_WORDLISTS)/$(1)-wordlist.$(EXT_CSV) \
		$(PATH_TEXTS)/$(1).$(EXT_ADJUSTMENT) \
		$(if $(findstring $(1),$(HAS_ILLUSTRATIONS)),$(PATH_TEXTS)/$(1).$(EXT_PICLIST)) \
		$(if $(findstring true,$(USE_HYPHENATION)),$(PATH_HYPHENATION)/$(FILE_HYPHENATION_TEX), ) \
		$(DEPENDENT_FILE_LIST)
	@echo INFO: Creating book PDF file: $(1).$(EXT_PDF)
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) $(1).$(EXT_TEX)
	$(call watermark,$$@)

#	cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) --no-pdf $(1).$(EXT_TEX)
#	cd $(PATH_PROCESS) && xdvipdfmx $(1).xdv

# Open the PDF file with reader
view-$(1) : $(PATH_PROCESS)/$(1).$(EXT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $$< &

# Open the SFM file with the text editor
edit-$(1) : $(PATH_TEXTS)/$(1).$(EXT_WORK)
	@ $(EDITSFM) $$< &

# Shortcut to open the PDF file
$(1) : $(PATH_PROCESS)/$(1).$(EXT_PDF)

# Rules for cleaning up content process files

# Remove the PDF for this component only
pdf-remove-$(1) :
	@echo INFO: Removing: $(PATH_PROCESS)/$(1).$(EXT_PDF)
	@rm -f $(PATH_PROCESS)/$(1).$(EXT_PDF)

# Make adjustment file which is a dependent of the PDF process
# Because every content file can have an adjustment file we
# automate this process by setting a dependency

adjlist-make-$(1) : $(PATH_TEXTS)/$(1).$(EXT_ADJUSTMENT)
	@echo INFO: Creating: $$<

# Call the adjustlist creation macro
$(PATH_TEXTS)/$(1).$(EXT_ADJUSTMENT) : $(PATH_TEXTS)/$(1).$(EXT_WORK)
ifeq ($(USE_ADJUSTMENTS),true)
	@$$(call makeadjlist,$(1))
else
	@echo INFO: USE_ADJUSTMENTS is set to \"$(USE_ADJUSTMENTS)\". $$@ not made.
endif

# Remove the adjustment file for this component only
adjlist-remove-$(1) :
ifeq ($(LOCKED),0)
	@echo Removing: $(1).$(EXT_ADJUSTMENT)
	@$$(call removeadjlist,$(1))
else
	@echo INFO: Cannot remove $(PATH_TEXTS)/$(1).$(EXT_ADJUSTMENT) because the project is locked.
endif

# Make the piclist file if there is a need for it with
# this component.
piclist-make-$(1) : $(PATH_TEXTS)/$(1).$(EXT_PICLIST)
	@echo INFO: Creating: $$<

# Make illustrations file if illustrations are used in this pub
# If there is a path/file listed in the illustrationsLib field
# this rule will create a piclist file for the book being processed.
# Also, the make_piclist_file.py script it will do the illustration
# file copy and linking operations. It is easier to do that in that
# context than in the Makefile context.
$(PATH_TEXTS)/$(1).$(EXT_PICLIST) : $(PATH_SOURCE_PERIPH)/$(FILE_ILLUSTRATION_CAPTIONS)
ifeq ($(USE_ILLUSTRATIONS),true)
	@$$(call makepiclist,$(1))
else
	@echo INFO: USE_ILLUSTRATIONS is set to \"$(USE_ILLUSTRATIONS)\". $$@ not made.
endif

# Remove the picture placement file for this component only
piclist-remove-$(1) :
ifeq ($(LOCKED),0)
	@echo Removing: $(1).$(EXT_PICLIST)
	@$$(call removepiclist,$(1))
else
	@echo INFO: Cannot remove: $(PATH_TEXTS)/$(1).$(EXT_PICLIST) because the project is locked.
endif

# Create a wordlist for a single book
$(PATH_WORDLISTS)/$(1)-wordlist.$(EXT_CSV) : | $(PATH_TEXTS)/$(1).$(EXT_WORK)
	@echo INFO: Creating: $$@
	@$$(call makewordlist,$(1))

# Command to create a wordlist for a single book
wordlist-make-$(1) : $(PATH_WORDLISTS)/$(1)-wordlist.$(EXT_CSV)

# Remove a wordlist for a single book
wordlist-remove-$(1) :
ifeq ($(LOCKED),0)
	@echo Removing: $(1)-wordlist.$(EXT_CSV)
	@$$(call removewordlist,$(1))
else
	@echo INFO: Cannot remove: $(PATH_WORDLISTS)/$(1)-wordlist.$(EXT_CSV) because the project is locked.
endif

# Set a wordlist for a single book as current
benchmark-wordlist-set-$(1) : $(PATH_WORDLISTS)/$(1)-wordlist.$(EXT_CSV)
ifeq ($(LOCKED),0)
	@echo Setting benchmark: $(1)-wordlist.$(EXT_CSV)
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "$(1)" "$(PATH_WORDLISTS)/$(1)-wordlist.$(EXT_CSV)" "" "set"
else
	@echo INFO: Cannot set benchmark: $(1)-wordlist.$(EXT_CSV) because the project is locked.
endif

# Benchmark test a wordlist for a single book
benchmark-wordlist-$(1) : $(PATH_WORDLISTS)/$(1)-wordlist.$(EXT_CSV)
	@echo Benchmark testing: $(1)-wordlist.$(EXT_CSV)
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "$(1)" "$(PATH_WORDLISTS)/$(1)-wordlist.$(EXT_CSV)" "" ""

# Benchmark test on the current component
benchmark-text-$(1) : | $(PATH_TEXTS)/$(1).$(EXT_WORK)
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "$(1)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" "" ""

# Set the current file as benchmark. This will overwrite
# whatever might currently be in the benchmark folder.
benchmark-text-set-$(1) :
ifeq ($(LOCKED),0)
	@echo Setting benchmark: $(1).$(EXT_WORK)
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "$(1)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" "" "set"
else
	@echo INFO: Cannot set benchmark: $(1).$(EXT_WORK) because the project is locked.
endif


# End of the content_rules define
endef

######################## End Main Macro ######################

####################### Start Main Process ###################

# Build a TeX control file that will process the components
# in a publication

# In case makefile needs things in order, we will put some
# dependent rules here before we hit the main content_rules
# building rule

# This builds a rule (in memory) for each of the content components
$(foreach v,$(GROUP_CONTENT),$(eval $(call content_rules,$(v))))

# WORD LIST COMMENTS
# Word lists will be made on the working files and will be rerun
# every time there is a change to one of them. In time we should
# have processes in place to do some checking against past lists
# to look for errors that may have happened in the

# Manual rule to create the master wordlist
make-master-wordlist : $(PATH_WORDLISTS)/$(FILE_MASTERWORDS)

# Create the master wordlist
$(PATH_WORDLISTS)/$(FILE_MASTERWORDS) : $(foreach v,$(GROUP_CONTENT),$(PATH_WORDLISTS)/$(v)-wordlist.$(EXT_CSV))
	@echo INFO: Creating: $@
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_MASTERWORDS)" "SYS" "" "$@" ""
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "SYS" "$(PATH_WORDLISTS)" "" ""

# HYPHENATION COMMENTS
# Hyphenation files are dependent on wordlist files but will
# not be rewritten every time there is a change in a wordlist.
# Once a hypheation file is in place it is expected that it will
# stay there and not be changed unless a problem is encountered.
# If the hyphenation is set to false then the files will not
# be created and a warning will be set in the terminal.

# Manual rule name for the creating the hypheation file
make-hyphen-wordlist: $(PATH_HYPHENATION)/$(FILE_HYPHENATION)

# Create the hypheation wordlist and link the log to the
# hypheation folder for easier access
$(PATH_HYPHENATION)/$(FILE_HYPHENATION) : | $(PATH_WORDLISTS)/$(FILE_MASTERWORDS)
ifeq ($(USE_HYPHENATION),true)
	@echo INFO: Creating: $@
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_HYPHENWORDS)" "SYS" "$(PATH_WORDLISTS)/$(FILE_MASTERWORDS)" "$@" ""
	@ln -sf $(PATH_LOG)/$(MOD_MAKE_HYPHENWORDS)-sys.log $(PATH_HYPHENATION)/
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "SYS" "$(PATH_HYPHENATION)/$(FILE_HYPHENATION)" "" ""
else
	@echo WARN: $(FILE_HYPHENATION) cannot be made because Hyphenation is set to \"$(USE_HYPHENATION)\"
endif

# Manual rule name for the creating the TeX hypheation file
# which controls hypheation for this publication.
make-tex-hyphens: $(PATH_HYPHENATION)/$(FILE_HYPHENATION_TEX)

# Create the TeX hypheation file. We will use the overwrite
# command because if any of the dependants have changed we
# will need to rewrite it (I think). If we did not use that
# the module would refuse to write out if the file existed.
$(PATH_HYPHENATION)/$(FILE_HYPHENATION_TEX) : $(PATH_HYPHENATION)/$(FILE_HYPHENATION) | \
		$(PATH_HYPHENATION)/$(FILE_LCCODELIST) \
		$(PATH_HYPHENATION)/$(FILE_HYCUSTOM) \
		$(PATH_HYPHENATION)/$(FILE_HYPREFIX) \
		$(PATH_HYPHENATION)/$(FILE_HYSUFFIX)
ifeq ($(USE_HYPHENATION),true)
	@echo INFO: Creating: $@
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEXHYPHEN)" "SYS" "$<" "$@" "overwrite"
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "SYS" "$(PATH_HYPHENATION)/$(FILE_HYPHENATION_TEX)" "" ""
else
	@echo WARN: $(FILE_HYPHENATION_TEX) cannot be made because Hyphenation is set to \"$(USE_HYPHENATION)\"
endif

# Rules for creating some of the hyphenation dependent files
$(PATH_HYPHENATION)/$(FILE_LCCODELIST) :
	@echo INFO: Creating: $@
	$(call copysmart,$(PATH_RESOURCES_HYPHENATION)/$(FILE_LCCODELIST),$@)

$(PATH_HYPHENATION)/$(FILE_HYCUSTOM) :
	@echo INFO: Creating: $@
	$(call copysmart,$(PATH_RESOURCES_HYPHENATION)/$(FILE_HYCUSTOM),$@)

$(PATH_HYPHENATION)/$(FILE_HYPREFIX) :
	@echo INFO: Creating: $@
	$(call copysmart,$(PATH_RESOURCES_HYPHENATION)/$(FILE_HYPREFIX),$@)

$(PATH_HYPHENATION)/$(FILE_HYSUFFIX) :
	@echo INFO: Creating: $@
	$(call copysmart,$(PATH_RESOURCES_HYPHENATION)/$(FILE_HYSUFFIX),$@)

# The rule to create the bible override style sheet. This is
# used to override styles for Scripture that come from the
# .project.sty file.
$(PATH_PROCESS)/$(FILE_TEX_STYLE) :
	$(call copysmart,$(PATH_RESOURCES_PROCESS)/$(FILE_TEX_STYLE),$@)

# Rule for building the TeX settings file that is used for
# format settings of all the main content. This is not to
# be confused with the Bible control file which is a TeX
# control file for processing the entire Bible.
$(PATH_PROCESS)/$(FILE_TEX_SETTINGS) : $(FILE_PROJECT_CONF)
	@echo INFO: Creating: $@
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEX)" "" "" "$@" ""

# Rule for building the GROUP_CONTENT control file. This is
# not the same as TeX settings file above.
$(PATH_PROCESS)/GROUP_CONTENT.tex :
	@echo INFO: Creating: $@
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEX)" "content" "content" "$@" ""

# Rule for generating the content components. It will
# also generate the TOC if that feature is turned on.
$(PATH_PROCESS)/GROUP_CONTENT.$(EXT_PDF) : \
		$(foreach v,$(GROUP_CONTENT), \
		$(PATH_TEXTS)/$(v).$(EXT_WORK) \
		$(PATH_TEXTS)/$(v).$(EXT_ADJUSTMENT) \
		$(if $(findstring $(v),$(HAS_ILLUSTRATIONS)),$(PATH_TEXTS)/$(v).$(EXT_PICLIST)) ) \
		$(PATH_WORDLISTS)/$(FILE_MASTERWORDS) \
		$(DEPENDENT_FILE_LIST) \
		$(if $(findstring true,$(USE_HYPHENATION)),$(PATH_HYPHENATION)/$(FILE_HYPHENATION_TEX), ) \
		$(PATH_PROCESS)/GROUP_CONTENT.tex
	@echo INFO: Creating: $@
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) GROUP_CONTENT.tex
	$(call watermark,$@)
	$(if $(findstring "toc",$(COMPONENTS_ALL)),@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TOC)")

# The TOC data is made during the content creation. As such
# the TOC file creation cannot happen until the content is made.
$(PATH_SOURCE_PERIPH)/$(FILE_TOC) : $(PATH_PROCESS)/GROUP_CONTENT.$(EXT_PDF)

# This enables preprocess checks on all the components processing each one independently.
preprocess-content :
	@echo INFO: Preprocess checking all content components:
	@$(foreach v,$(GROUP_CONTENT), $(call preprocessing,$(v),$($(v)_content)) )

# This enables postprocesses on all the components processing each one independently.
postprocess-content :
ifeq ($(LOCKED),0)
	@echo INFO: Postprocessing all content components
	@$(foreach v,$(GROUP_CONTENT), $(call postprocessing,$(v),$($(v)_content)) )
	$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "SYS" "$(PATH_TEXTS)" "" ""
else
	@echo INFO: Cannot post process: $(PATH_TEXTS)/$(1).$(EXT_WORK) because the project is locked.
endif

# Do a component section and veiw the resulting output
view-content : $(PATH_PROCESS)/GROUP_CONTENT.$(EXT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

pdf-remove-content :
	@echo INFO: Removing file: $(PATH_PROCESS)/GROUP_CONTENT.$(EXT_PDF)
	@rm -f $(PATH_PROCESS)/GROUP_CONTENT.$(EXT_PDF)


###############################################################
#			Shared functions
###############################################################

# Run preprocesses on the source text.
define preprocessing
@if test -r "$(PATH_TEXTS)/$(1).$(EXT_WORK)"; then \
	echo INFO: Removing: $(PATH_TEXTS)/$(1).$(EXT_WORK); \
	rm -f $(PATH_TEXTS)/$(1).$(EXT_WORK); \
fi
@echo INFO: Preprocessing: '$(PATH_SOURCE)/$(2)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE)'
@$(MOD_RUN_PROCESS) "preprocessChecks" "$(1)" "$(PATH_SOURCE)/$(2)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" ""
endef

# Run the postprocesses on working text, however, to be safe
# we run the preprocesses as well.
define postprocessing
$(call preprocessing ,$(1),$($(1)_content))
@echo INFO: Copy to: "$(PATH_TEXTS)/$(1).$(EXT_WORK)"
@$(MOD_RUN_PROCESS) "$(MOD_IMPORT)" "$(1)" "$(PATH_SOURCE)/$(2)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" ""
@echo INFO: Postprocessing: '$(PATH_TEXTS)/$(1).$(EXT_WORK)'
@$(MOD_RUN_PROCESS) "textProcesses" "$(1)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" ""
endef

# Create a single adjustment file if adjustments are turned on
makeadjlist = $(MOD_RUN_PROCESS) "$(MOD_PARA_ADJUST)" "$(1)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" "$(PATH_TEXTS)/$(1).$(EXT_ADJUSTMENT)"

# Create a single piclist file if illustrations are turned on
makepiclist = $(MOD_RUN_PROCESS) "$(MOD_MAKE_PICLIST)" "$(1)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" "$(PATH_TEXTS)/$(1).$(EXT_PICLIST)"

# Remove a single piclist file
removepiclist = rm -f $(PATH_TEXTS)/$(1).$(EXT_PICLIST)

# Remove a single adjustment file
removeadjlist = rm -f $(PATH_TEXTS)/$(1).$(EXT_ADJUSTMENT)

# Create a single wordlist - As these tests can be run multiple
# times in short succession, we will not do benchmark testing
# on single lists. We'll rely on the master wordlist benchmark
# test to find problems
makewordlist = $(MOD_RUN_PROCESS) "$(MOD_MAKE_WORDLIST)" "$(1)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" "$(PATH_WORDLISTS)/$(1)-wordlist.$(EXT_CSV)"

# Remove a single wordlist
removewordlist = rm -f $(PATH_WORDLISTS)/$(1)-wordlist.$(EXT_CSV)

##############################################################
#			Rules for handling piclist file creation
##############################################################

# Rule to make all the piclist files at one time
piclist-make-all :
ifeq ($(LOCKED),0)
	@for v in $(GROUP_CONTENT); do $(call makepiclist,$$v); done
else
	@echo INFO: Cannot create the piclist files because the project is locked
endif

# Rule to remove all piclist files at one time if the project is not locked
piclist-remove-all :
ifeq ($(LOCKED),0)
	@echo INFO: Now removing all piclist files
	@for v in $(GROUP_CONTENT); do $(call removepiclist,$$v); done
else
	@echo INFO: Cannot remove the piclist files because the project is locked
endif

# Copy into place the captions.csv file that goes in the
# project peripheral folder located in the Source folder.
$(PATH_SOURCE_PERIPH)/$(FILE_ILLUSTRATION_CAPTIONS) :
ifeq ($(USE_ILLUSTRATIONS),true)
	$(call copysmart,$(PATH_RESOURCES_ILLUSTRATIONS)/$(FILE_ILLUSTRATION_CAPTIONS),$@)
endif

#################################################################################

# Create all the adjustment files
# This will not work right if the working files have not been
# created before it is started
adjlist-make-all :
ifeq ($(LOCKED),0)
	@echo INFO: Creating all adjustment files:
	@for v in $(GROUP_CONTENT); do $(call makeadjlist,$$v); done
else
	@echo INFO: Cannot create the adjustment files because the project is locked
endif

# Remove all the adjustment files
adjlist-remove-all :
ifeq ($(LOCKED),0)
	@echo INFO: Removing all adjustment files:
	@for v in $(GROUP_CONTENT); do $(call removeadjlist,$$v); done
else
	@echo INFO: Cannot remove the adjustment files because the project is locked
endif

#################################################################################

# GLOBAL BENCHMARK TESTS

# Most of these are automated but these commands are for the GUI.

# Test all the working text against the stored benchmark text
benchmark-text-all :
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "SYS" "$(PATH_TEXTS)" "" ""

# Test the Hyphenation folder
benchmark-hyphen-tex : | $(PATH_HYPHENATION)/$(FILE_HYPHENATION_TEX)
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "SYS" "$(PATH_HYPHENATION)/$(FILE_HYPHENATION_TEX)" "" ""

# Set the current TeX hyphenation to be the benchmark
benchmark-hyphen-set-tex : | $(PATH_HYPHENATION)/$(FILE_HYPHENATION_TEX)
ifeq ($(LOCKED),0)
	@echo Setting benchmark: $(FILE_HYPHENATION_TEX)
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "SYS" "$(PATH_HYPHENATION)/$(FILE_HYPHENATION_TEX)" "" "set"
else
	@echo INFO: Cannot set benchmark: $(FILE_HYPHENATION_TEX) because the project is locked.
endif

# Test the hyphenation wordlist file
benchmark-hyphen-txt : | $(PATH_HYPHENATION)/$(FILE_HYPHENATION)
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "SYS" "$(PATH_HYPHENATION)/$(FILE_HYPHENATION)" "" ""

# Set the current hyphenation wordlist file to be the benchmark
benchmark-hyphen-set-txt : | $(PATH_HYPHENATION)/$(FILE_HYPHENATION)
ifeq ($(LOCKED),0)
	@echo Setting benchmark: $(FILE_HYPHENATION_TEX)
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "SYS" "$(PATH_HYPHENATION)/$(FILE_HYPHENATION)" "" "set"
else
	@echo INFO: Cannot set benchmark: $(FILE_HYPHENATION) because the project is locked.
endif

# Test the Hyphenation folder
benchmark-hyphen-all : | $(PATH_HYPHENATION)/$(FILE_HYPHENATION_TEX)
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "SYS" "$(PATH_HYPHENATION)" "" ""

# Test the Wordlist master file
benchmark-wordlist-master : | $(PATH_WORDLISTS)/$(FILE_MASTERWORDS)
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "SYS" "$(PATH_WORDLISTS)/$(FILE_MASTERWORDS)" "" ""

# Set the master wordlist for project
benchmark-wordlist-set-master : | $(PATH_WORDLISTS)/$(FILE_MASTERWORDS)
ifeq ($(LOCKED),0)
	@echo Setting benchmark: $(FILE_MASTERWORDS)
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "SYS" "$(PATH_WORDLISTS)/$(FILE_MASTERWORDS)" "" "set"
else
	@echo INFO: Cannot set benchmark: $(1)-wordlist.$(EXT_CSV) because the project is locked.
endif

# Test the Wordlists folder
benchmark-wordlist-all : | $(PATH_WORDLISTS)/$(FILE_MASTERWORDS)
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "SYS" "$(PATH_WORDLISTS)" "" ""
