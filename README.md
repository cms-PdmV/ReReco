> [!IMPORTANT]  
> This repository has been migrated to the PPD Technical Support team inside the CERN GitLab instance: [ReReco](https://gitlab.cern.ch/cms-ppd/technical-support/web-services/ReReco). Please open and follow issues directly there, do not open or follow them here!

# ReReco machine

Web based tool for Data ReReco production management

### Introduction
ReReco machine is a web-based tool for creating, submitting and bookkeeping reprocessing workflows - ReReco requests. Only PdmV conveners have rights to perform actions in the ReReco machine.

### Links
- ReReco Machine: https://cms-pdmv-prod.web.cern.ch/rereco/
- ReReco Machine (Development version): https://cms-pdmv-dev.web.cern.ch/rereco/
- GitHub Repository: https://github.com/cms-PdmV/ReReco
- GitHub issues/feature requests: https://github.com/cms-PdmV/ReReco/issues

## Overview

### Structure and navigation
ReReco machine has six different pages - Home (Initial page), Subcampaigns, Tickets, Requests, Dashboard and Editing/Creating new. First five pages can be reached by clicking buttons at the top bar - click ReReco logo to get to Home page or use other four appropriately named buttons. The Editing/Creating new page depends on the context, i.e. it can be accessed only from Subcampaigns, Tickets and Requests pages and allow actions on these objects.

### Users
There are three kinds of user roles in the ReReco machine: User, Manager and Administrator. The role can be determined by looking for a star next to the person's name in the top bar. If there is no star, user is a User, if star is yellow, user is a Manager and if it's blue, user is an Administrator. Role can also be seen in a tooltip when hovering over user's name.
User roles are controlled by E-Groups. Manager role requires membership of "cms-ppd-conveners-pdmv" e-group, Administrator role requires membership of "cms-pdmv-serv" e-group.
- User - can browse ReReco machine, use search, look at subcampaigns, requests and tickets, cmsDriver commands. Basically users are free to browse, but are not allowed to do any persistent changes.
- Manager - can do same actions as User. Managers can also create, delete and update Subcampaigns, Tickets and Requests, submit and reset Requests. Managers have access to all the ReReco machine functions and can perform all actions. Some actions are allowed to the Managers, but buttons are hidden as they should not be needed for normal operation.
- Administrators - can do same actions as Manager. Administrators do not have any special powers, they just see more debug output and have a couple of buttons to perform actions that should be done automatically, e.g. force refresh from Stats2.

## Home (Initial Page)

### Introduction
Home page provides a search across all objects in the ReReco machine, a couple of links to quickly see newest items in the machine as well as overview of number of objects in the database with more details on submitted Requests.

### Search
Whenever a query is entered into the search field, ReReco machine performs multiple searches on multiple attributes across all three types of objects in the database.

Currently these attributes are included in the search:
- PrepID of Subcampaigns, Tickets and Requests
- Subcampaign of Tickets and Requests
- Processing string of Tickets and Requests
- Input datasets and requests of Tickets
- Input dataset of Requests
- Output datasets of Requests
- Workflows (in ReqMgr2) of Requests

Search supports wildcards, i.e. asterisks (\*) as any number of any characters, e.g. `A*C` would match `AC`, `ABC`, `ABBC`, etc. Space character is automatically translated to an asterisk and both can be used interchangeably. Search is based on regex, however it is not guaranteed to support full regex functionality.

Search results is a list of three values: found value on the left and database and attribute name on the right in a format `database:attribute`. When user clicks on a search result, user will be directed to the page indicated in the `database` part and results that match the criteria `attribute=value` will be shown. 

Example 1: user types `ABC` in the search field and is presented with a search result that has value `ABCD` (on the left) and `requests:processing_string` as database and the attribute (on the right). If user clicks on this result, all Requests that have processing string "ABCD" will be shown.

Example 2: user types `/HIDoubleMuon/HIRun2018A-04Apr2019-v1/AOD` in the search field and is presented with a search result that has value `/HIDoubleMuon/HIRun2018A-04Apr2019-v1/AOD` (on the left) and `requests:input_dataset` on the right. If user clicks on this result, all Requests that have "/HIDoubleMuon/HIRun2018A-04Apr2019-v1/AOD" as input dataset will be shown.

### Quick links
Quick links allow quick access to ticket creation page or to requests or tickets pages where items are sorted by creation date with newest at the top.

### Objects in ReReco database 
This section provides quick access to each type of objects (Subcampaigns, Tickets and Requests) as well as show how many Tickets and Requests are in the database. Tickets and Requests are expanded to show number of items with a particular status. Requests that have status "submitted" are expanded to even more granularity and show how many Requests with different processing strings are submitted. Items in the "submitted Requests" list are sorted by number of Requests with given processing string.

Clicking on links will lead to pages of items of that type with that particular status (and processing string).

## Subcampaigns

### Introduction
Campaigns on computing side group together a big number of similar requests. This concept is also used in the ReReco machine where it is not only used to group, but also to act as a template for the requests. It would be tedious to create tens or hundreds of identical requests where only the input dataset is different. Such template can store the cmsDriver.py command values and requests then can be created by taking an input dataset and the cmsDriver.py. This way arguments are defined only once and can be reused multiple times. Unfortunately "Computing Campaigns" cannot be directly used in the ReReco machine because even though a campaign groups similar requests, it can contain different primary datasets and, subsequently, fundamentally different cmsDriver.py commands, e.g. "UltraLegacy2017" campaign could be used for both "Cosmics" and "ZeroBiasScouting" requests and their cmsDriver.py attributes are very different. This means that after submitting "Cosmics", the template would have to be discarded and created from scratch for "ZeroBiasScouting". If "Cosmics" had to be submitted again, then template once again would have to be scrapped and recreated. This is why it was decided to introduce a smaller unit of "Campaign" in ReReco machine - a subcampaign. Subcampaign still represents one of the campaigns in computing, but different subcampaigns can have different cmsDriver.py and not conflict with each other. In the example mentioned above, there would be two UltraLegacy2017 subcampaigns - one for Cosmics and one for ZeroBiasScouting. This way ReReco machine can preserve different cmsDriver.py arguments that are used in a single computing campaign. This is why this is called a subcampaign - it is like one snapshot of a campaign. subcampaign name is not submitted to computing, requests that are submitted to computing, use campaign name that given subcampaign is part of, so this new object type does not affect anything outside the ReReco machine.

Subcampaigns in the ReReco machine: https://cms-pdmv-prod.web.cern.ch/rereco/subcampaigns

### Subcampaign naming
It is important to understand how subcampaigns are and should be named. subcampaign name is always made of two parts that are joined with a dash ( - minus). First part is the campaign name in computing. Second part is subcampaign's identifier - string that gives more insight on what is the purpose of given subcampaign.

All available computing campaigns and their names: https://github.com/CMSCompOps/WmAgentScripts/blob/master/campaigns.json

If needed name is not there, user needs to first announce the new campaign to computing, inject a pilot request, wait for its completion and then ask for the activation of the campaign.

Names of two example subcampaigns mentioned in the Introduction section would be: "UltraLegacy2017-Cosmics" and "UltraLegacy2017-ZeroBiasScouting" where "UltraLegacy2017" is the computing campaign name and "Comics" and "ZeroBiasScouting" are subcampaign identifiers.

Some examples of existing subcampaigns:
- UltraLegacy2018-LowMass
  - Computing campaign: UltraLegacy2018
  - Subcampaign identifier: LowMass
- NANOAODRun2DataProd-NanoAODv7_2016
  - Computing campaign: NANOAODRun2DataProd
  - Subcampaign identifier: NanoAODv7_2016
- MiniAODHI18Data-Winter2021
  - Computing campaign: MiniAODHI18Data
  - Subcampaign identifier: Winter2021

### Subcampaign attributes
- PrepID (`prepid`) - unique identifier of the subcampaign. Made of two parts joined with a dash. Refer to "Subcampaign naming" section for more info.
- CMSSW Release (`cmssw_release`) - CMSSW Release name that will be used in all requests created from this campaign. Name must follow the `CMSSW_X_Y_Z[_abc]` pattern
- Energy (`energy`) - energy in TeV, will be propagated the the created requests
- History (`history`) - history of actions performed on the subcampaign, such as creation or editing. Each entry includes date, user username, action and value
- Memory (`memory`) - memory in MB, will be propagated to the created requests
- Notes (`notes`) - free-form user text
- Runs JSON Path (`runs_json_path`) - path where DCS JSON file is located, this path will be prepended by "https://cms-service-dqmdc.web.cern.ch/CAF/certification/", so this attribute should be something like "Collisions17/13TeV/DCSOnly/json_DCSONLY_LowPU_eraH.txt"
- Sequences (`sequences`) - list of cmsDriver sequence arguments that will be propagated to the created requests

### Subcampaign actions
- Edit - open editing page of the subcampaign
- Delete - delete the subcampaign. This is allowed only if there are no requests and no tickets with given subcampaign. If there are, they have to be deleted first
- Clone - open a form to create a new subcampaign and prefill form fields with info of given subcampaign
- Show requests - show requests that belong to this subcampaign

## Tickets

### Introduction
Tickets are the way to easily create a set of requests in a certain subcampaign or chain of subcampaigns where output of one request is input for the next one. Ticket itself is a one-use-only object - when ticket is created, it can be then used to create requests and after that it is there only for the bookkeeping purposes. If new requests need to be created, a new ticket must be created. Two fundamental ingredients for a ticket are list of input datasets or requests and subcampaign.

Ticket can use either datasets or existing requests as input. List can can be a mix of both.

### Getting datasets from DBS
In order to ease up getting list of input datasets, ReReco machine offers a function to query the DBS. To do so, user has to click "Query for datasets" button at the bottom which will show a popup.

In the popup user has two fields: query and comma-separated values to filter out. In the first field user must enter a query, usually with wildcards. It must satisfy such format "/*/*/DATATIER", e.g. /*Electron*/Run2016A-v*/RAW. However, this could include datasets that were produced by validation or pilot requests. In order to remove such datasets, user can specify "validation,pilot" in the second field. This field is a list of comma-separated values that will be used when filtering-out the datasets. If field has "validation,pilot", it means that after fetching the dataset names, all names that have either "validation" or "pilot" in them, will be removed. Note that these values are case sensitive. Some primary datasets are blacklisted in the ReReco machines, which means that dataset names with these primary datasets will be implicitly removed from the fetch results.

The blacklist can be found here: https://cms-pdmv-prod.web.cern.ch/rereco/api/settings/get/dataset_blacklist 

If list of datasets is not empty, user will have two options what to do with existing datasets: "Fetch and replace" will fetch dataset list from DBS and replace existing list or "Fetch and append" will fetch dataset list and append it to already existing list. If user chooses to append, only datasets that are not in existing list will be appended, i.e. appending will not duplicate dataset names.

### Getting PrepIDs of existing requests
In order to ease up getting list of input requests, just like input datasets, ReReco machine has a helper to search for and fetch PrepIDs of already existing requests. Popup for fetching can be opened by clicking "Query for requests" button at the bottom.

This feature will search ReReco machine database for requests based on user given query. Just like with datasets, there are buttons to "Fetch and replace" or to "Fetch and append".

Due to performance reasons result size is limited to 1000 PrepIDs.

### Ticket steps
ReReco machine allows to create tickets with one or multiple steps. Steps represent requests in different campaigns where output of one request will be used as input for the subsequent request. For example, first step can produce AOD and MiniAOD datasets in subcampaign A and seconds step can then use MiniAOD as input and produce NanoAOD dataset in subcampaign B. Each step has a subcampaign, processing string, list of sizes per event (same number of values as there are sequences in subcampaign), list of times per event (same number of values as there are sequences in subcampaign) and priority. All of these attribute will be propagated to the created request and sequences will be copied from subcampaign to the request.

### Creating requests
When user clicks a button to create requests, ReReco machine will go over list of input datasets or request PrepIDs and for each of them will create as many requests as there are steps and set input of requests appropriately. For example, if there are two steps, first one has Subcampaign1 and second has Subcampaign2 and three datasets: AAA, BBB and CCC. ReReco machine will create six requests: three in Subcampaign1 with AAA, BBB and CCC as input and another three in Subcampaign2 with the first ones as input respectively. 

### Ticket attributes
- PrepID (`prepid`) - unique identifier of the ticket
- Created requests (`created_requests`) - list of PrepIDs of requests that were created from this ticket
- History (`history`) - history of actions performed on the ticket, such as creation or editing. Each entry includes date, user username, action and value
- Input (`input`) - list of input dataset names or request PrepIDs that will be used as input
- Notes (`notes`) - free-form user text
- Status (`status`) - ticket status, can be either new or done
- Steps (`steps`) - list of dictionaries that have subcampaign name, processing string, sizes and times per event values that will be used to create "chains" of requests

### Ticket actions
- Edit - open editing page of the ticket
- Delete - delete the ticket. This is allowed only if it is new or if all requests, that were created from the ticket are deleted. If the requests are present, they have to be deleted first
- Clone - open a form to create a new ticket and prefill form fields with info of given ticket
- Create requests - create requests for each input dataset or request and each step
- Show requests - show requests that were created from the ticket
- TWiki - open a snippet that can be copied to ReReco TWiki. Snippet forms tables of eras with each row having a primary dataset name, link to historical pMp plot and list of runs

## Requests

### Introduction
Requests are the main objects in the machine. Each request represent a single or multiple cmsDriver.py commands that are called a "sequences" as well as hold some metadata. Requests are the units of work that will be submitted to computing as jobs.

### Request status
#### Statuses
Unlike other objects in ReReco machine, requests have multiple different statuses. They are (in order):
- New - this is request's initial state. Most of the attributes can be edited or the request itself can be deleted. Request can also have it's "Options reset"
- Approved - this "freezes" request values and acts as a last step before submission to computing. If request has another request as input, output dataset is taken from input request and set as input dataset of the request
- Submitting - request is either in queue to be submitted or is currently being submitted (running cmsDriver.py and uploading JobDict to ReqMgr2). Whether it is in the queue or being submitted can be seen in the Dashboard
- Submitted - request was submitted for production in computing. Workflows (requests in ReqMgr2) can be seen in "Workflows" column
- Done - request successfully ran in computing and finished. Workflows are in announced or normal-archived status and all output datasets are in VALID status. There are no subsequent steps

#### Moving to next status ("Next" button)
- New -> approved - if input is set to a request X, output dataset of request X will be set as input dataset
- Approved -> submitting - puts request in submission queue that can be seen in the Dashboard
- Submitted -> done - can be either moved by user or by periodic script when last workflow is announced or normal-archived and output datasets are VALID

#### Moving to previous status ("Previous" button)
- Approved -> new - sets status to new
- Submitted -> approved - rejects workflows in ReqMgr2, resets total events and completed events to 0 and clears ConfigCacheID in the sequences. Output datasets are NOT invalidated
- Done -> new - moves request to approved and then back to new status, same actions as Submitted -> approved -> new are performed

### Getting runs and lumisection ranges
It is possible to automatically fetch list of runs and lumisection ranges in request editing page.

"Get runs" will fetch all runs of input dataset and, if subcampaign's Runs JSON path is set, will intersect them with runs in the Runs JSON file. If subcampaign does not have Runs JSON path set, all runs of input dataset will be used. List of runs will appear in "Runs" field.

If subcampaign's Runs JSON path is set, "Get lumisections" will take list of runs of "Runs" field and intersect them with Runs JSON file and return lumisection ranges from the Runs JSON file. If subcampaign's Runs JSON path is not set, empty dictionary of lumisection ranges will be returned. If "Runs" field was edited and has different runs than what would be returned by "Get runs", specified runs will be used for the intersection, even if they do not appear in the input dataset. 

This will be automatically done when requests are created from the ticket.

### Request submission

If request has only one sequence, it will be submitted with RequestType set toReReco and the whole workflow would represent a single task.

If request has more than one sequence, it will be submitted with RequestType set to TaskChain and each sequence will appear as a Task in the Job Dictionary.

### Request priority
Request's priority can be changed at any time before it is done.

If request is submitted, priority change in editing page will also change workflow priority in the ReqMgr2.

If priority is changed directly in ReqMgr2 or somewhere else outside the ReReco machine, it will be updated in the machine during the next update from Stats2.

### Request attributes
- PrepID (`prepid`) - unique identifier of the request
- CMSSW release (`cmssw_release`) - CMSSW Release that will be used to generate configs and run the job
- Completed events (`completed_events`) - number of events of the last output dataset that were produced so far
- Energy (`energy`) - energy in TeV
- History (`history`) - history of actions performed on the request, such as creation, submission or editing. Each entry includes date, user username, action and value
- Input (`input`) - input can be either request or dataset. If input is another request, then the value is it's prepid, if input is a dataset, then it's dataset name
- Lumisections (`lumisections`) - dictionary of runs as keys and lumisection ranges as values
- Memory (`memory`) - memory in MB, to be provided to computing
- Notes (`notes`) - free-form user text
- Output datasets (`output_datasets`) - list of output datasets fetched from Stats2 (ReqMgr2)
- Priority (`priority`) - request priority, to be provided to computing during submission. If this is changed when request is submitted , new priority will be set in ReqMgr2 too
- Processing string (`processing_string`) - processing string of the request
- Runs (`runs`) - list of runs to be processed. If Lumisections is not empty, runs will not be included in the Job Dict
- Sequences (`sequences`) - list of sequences (cmsDriver.py commands and their attributes)
- Size per event (`size_per_event`) - list of size per event values (same number of values as sequences) to be provided to computing, each size per event corresponds to one sequence
- Status (`status`) - request status
- Subcampaign (`subcampaign`) - subcampaign that request is member of
- Time per event (`time_per_event`) - list of time per event values (same number of values as sequences) to be provided to computing, each time per event corresponds to one sequence
- Total events (`total_events`) - number of expected to be processed events, fetched from Stats2 (ReqMgr2)
- Workflows (`workflows`) - list of workflows in computing and their output datasets

### Request actions
- Edit - open editing page of the request
- Delete - delete this request. Requests can be deleted only if their status is "new"
- Clone - open a form to create a new request and prefill form fields with info of given request
- cmsDriver - open a simple-text page with CMSSW environment setup and cmsDriver.py commands of the request
- Job dict - open a simple-text page that contains the JSON that will be/is submitted to the ReqMgr2
- Previous - move request to previous status
- Next - move request to next status
- Create ticket - (only at the bottom, when multiple requests are selected) open Ticket creation form with selected requests placed as Input
- Option reset - available only when request is in "new" status, this overwrites request's memory, sequences and energy with ones from the subcampaign (for example, if subcampaign was updated after request was created)
- Update from Stats2 - manually pull workflow information from Stats2
- Stats2 - open Stats2 page with all workflows of the request

## Sequences (cmsDriver.py)

### Introduction
Sequence represents a single cmsDriver.py command.

### Harvesting
If sequence has a `DQM` step, additional harvesting step (cmsDriver.py) will be created. If `DQM` step has additional specification in a form of `--step DQM:XYZ`, harvesting step will have the same format - `--step HARVESTING:XYZ`.

### ALCA/SKIM steps
If sequence has `ALCA` or `SKIM` step that do not have additional specification, i.e. not `ALCA:XYZ` and not `SKIM:ABC`, but are just `ALCA` and/or `SKIM` then these steps will have `:@Dataset` added (where `{Dataset}` is the primary dataset of the request) if primary dataset is present in `AlCaRecoMatrix` dictionary in `Configuration.AlCa.autoAlca` and `autoSkim` dictionary in `Configuration.Skimming.autoSkim` respectively. If primary dataset is not in the mentioned dictionaries, step will be removed completely.

For example, request's primary dataset is `HLTPhysics` and steps in sequence are like this `--step ALCA,SKIM`. Then, if `HLTPhysics` is present in `AlCaRecoMatrix` dictionary, `ALCA` step will become `ALCA:@HLTPhysics` and if `HLTPhysics` is in `autoSkim` dictionary, `SKIM` will become `SKIM:@HLTPhysics`. In the end it will look like `--step ALCA:@HLTPhysics,SKIM:@HLTPhysics`.

If these steps already have specification as `:ABC`, they will be left as is, e.g. `--step ALCA:AAA` will be kept as `--step ALCA:AAA`.

### Sequence attributes
- Conditions (`conditions`) - cmsDriver.py argument `--conditions`
- Customise (`customise`) - cmsDriver.py argument `--customise`
- Datatier (`datatier`) - cmsDriver.py argument `--datatier`, list of comma separated datatiers
- Era (`era`) - cmsDriver.py argument `--era`
- Eventcontent (`eventcontent`) - cmsDriver.py argument `--eventcontent`, list of comma separated event contents
- Extra (`extra`) - additional arguments that will be added to the end of built cmsDriver command, e.g. `--runUnscheduled` or `--data`
- GPU (gpu.requires) - indicate whether GPU parameters should be added to Job Dict. Possible values: forbidden, optional, required
- GPU Parameters (more info: https://github.com/dmwm/WMCore/wiki/GPU-Support#gpu-parameter-specification):
  - GPU Memory (gpu.gpu_memory) - memory in MB
  - CUDA Capabilities (gpu.cuda_capabilities) - comma separated values
  - CUDA Runtime (gpu.cuda_runtime) - ?
  - GPU Name (gpu.gpu_name) - ?
  - CUDA Driver Version (gpu.cuda_driver_version) - ?
  - CUDA Runtime Version (gpu.cuda_runtime_version) - ?
- nThreads (`nThreads`) - cmsDriver.py argument `--nThreads`, number of CPU cores to use in production
- Scenario (`scenario`) - cmsDriver.py argument `--scenario`, one of predefined values: `pp`, `cosmics`, `nocoll` or `HeavyIons`
- Step (`step`) - cmsDriver.py argument `--step`, list of comma separated steps

## Dashboard

### Submission threads
A single Request submission might take up to 10 minutes, so they are done in ReReco machine's background threads, called workers. Workers are independent of user presence, so if user pushes request to status submitting and immediately goes offline, request will still be submitted by these background workers. Otherwise submission would rely on user and ReReco machine having an active connection for each Request while it is being submitted.

In the Dashboard, "Submission threads" shows current size and occupancy of the submission worker pool. Pool size is dynamic and can expand to concurrent 15 threads or shrink to 0, depending on amount of Requests to be submitted.

### Submission queue
Submission queue shows list of PrepIDs of Requests that are waiting to be submitted.
