<template>
  <div>
    <h1 class="page-title" v-if="creatingNew"><span class="font-weight-light">Creating</span> new ticket</h1>
    <h1 class="page-title" v-else><span class="font-weight-light">Editing ticket</span> {{prepid}}</h1>
    <v-card raised class="page-card">
      <table v-if="editableObject">
        <tr>
          <td>PrepID</td>
          <td><input type="text" v-model="editableObject.prepid" :disabled="!editingInfo.prepid"></td>
        </tr>
        <tr>
          <td>Job dict overwrite</td>
          <td>
            <span class="show-job-dict-overwrite" v-if="!showJobDictOverwrite" v-on:click="toggleJobDictOverwrite()">Edit</span>
            <JSONField v-show="showJobDictOverwrite" v-model="editableObject.job_dict_overwrite" :disabled="!editingInfo.job_dict_overwrite"/>
          </td>
        </tr>
        <tr>
          <td>Steps ({{listLength(editableObject.steps)}})</td>
          <td>
            <div v-for="(step, index) in editableObject.steps" :key="index">
              <h3>Step {{index + 1}}</h3>
              <table>
                <tr>
                  <td>Subcampaign</td>
                  <td>
                    <autocompleter
                      v-model="step.subcampaign"
                      :identifier="'Step' + index"
                      :getSuggestions="getSubcampaignSuggestions"
                      :onBlur="getSubcampaign"
                      :onSelect="getSubcampaign"
                      :disabled="!editingInfo.steps[index].subcampaign">
                    </autocompleter>
                  </td>
                </tr>
                <tr>
                  <td>Processing string</td>
                  <td><input type="text"
                             v-model="step.processing_string"
                             :disabled="!editingInfo.steps[index].processing_string"></td>
                </tr>
                <tr v-if="step.size_per_event.length">
                  <td>Size per event</td>
                  <td>
                    <div v-for="(sizePerEvent, sizePerEventIndex) in step.size_per_event" :key="sizePerEventIndex" >
                      <input type="number"
                             style="margin-top: 2px"
                             v-model="step.size_per_event[sizePerEventIndex]"
                             :disabled="!editingInfo.steps[index].size_per_event">kB
                    </div>
                  </td>
                </tr>
                <tr v-if="step.time_per_event.length">
                  <td>Time per event</td>
                  <td>
                    <div v-for="(timePerEvent, timePerEventIndex) in step.time_per_event" :key="timePerEventIndex">
                      <input type="number"
                             style="margin-top: 2px"
                             v-model="step.time_per_event[timePerEventIndex]"
                             :disabled="!editingInfo.steps[index].time_per_event">s
                    </div>
                  </td>
                </tr>
                <tr>
                  <td>Priority</td>
                  <td><input type="number"
                             v-model="step.priority"
                             :disabled="!editingInfo.steps[index].priority"></td>
                </tr>
              </table>
              <v-btn small
                     class="mr-1 mb-1"
                     color="error"
                     v-if="(creatingNew || index != 0) && editingInfo.__steps"
                     @click="deleteStep(index)">Delete step {{index + 1}}</v-btn>
              <hr>
            </div>
            <v-btn small
                   class="mr-1 mb-1 mt-1"
                   color="primary"
                   v-if="editingInfo.__steps && editableObject.steps.length < 5"
                   @click="addStep()">Add step {{listLength(editableObject.steps) + 1}}</v-btn>
          </td>
        </tr>
        <tr>
          <td>Notes</td>
          <td><textarea v-model="editableObject.notes" :disabled="!editingInfo.notes"></textarea></td>
        </tr>
        <tr>
          <td>Input ({{listLength(editableObject.input)}})</td>
          <td><textarea v-model="editableObject.input" :disabled="!editingInfo.input"></textarea></td>
        </tr>
      </table>
      <v-btn small class="mr-1 mt-1" color="primary" @click="save()" :disabled="!listLength(editableObject.steps) || !listLength(editableObject.input)">Save</v-btn>
      <v-btn v-if="editingInfo.input" small class="mr-1 mt-1" color="primary" @click="showGetDatasetsDialog()">Query for datasets</v-btn>
      <v-btn v-if="editingInfo.input" small class="mr-1 mt-1" color="primary" @click="showGetRequestsDialog()">Query for requests</v-btn>
      <v-btn small class="mr-1 mt-1" color="error" @click="cancel()">Cancel</v-btn>
    </v-card>
    <v-dialog v-model="getDatasetsDialog.visible"
              max-width="50%">
      <v-card class="page-card mb-0" style="max-width: none !important;">
        <v-card-title class="headline">Fetch dataset list</v-card-title>
        <v-card-text>
          Fetch a list of input datasets from DBS. Query must satisfy this format:<pre>/*/*/DATATIER</pre>
          <input type="text" v-model="getDatasetsDialog.input" class="mb-2" placeholder="Dataset name query, for example /ZeroBias/Run2018*/RAW">
          Comma-separated list of values to use when filtering-out dataset names:
          <input type="text" v-model="getDatasetsDialog.exclude" placeholder="Comma separated patterns to exclude, e.g. validation,pilot">
        </v-card-text>
        <small style="opacity: 0.4">Note: some primary datasets are blacklisted and will not appear in fetched list</small>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn small class="mr-1 mb-1" color="primary" v-if="!listLength(editableObject.input)" :disabled="!getDatasetsDialog.input.length" @click="getDatasets(true)">Fetch</v-btn>
          <v-btn small class="mr-1 mb-1" color="primary" v-if="listLength(editableObject.input)" :disabled="!getDatasetsDialog.input.length" @click="getDatasets(true)" title="Fetch list and replace existing list with newly fetched one">Fetch and replace</v-btn>
          <v-btn small class="mr-1 mb-1" color="primary" v-if="listLength(editableObject.input)" :disabled="!getDatasetsDialog.input.length" @click="getDatasets(false)" title="Fetch list and append it to an existing list">Fetch and append</v-btn>
          <v-btn small class="mr-1 mb-1" color="error" @click="closeGetDatasetsDialog()">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="getRequestsDialog.visible"
              max-width="50%">
      <v-card class="page-card mb-0" style="max-width: none !important;">
        <v-card-title class="headline">Fetch request list</v-card-title>
        <v-card-text>
          Fetch a list of request PrepIDs from ReReco machine
          <input type="text" v-model="getRequestsDialog.input" class="mb-2" placeholder="PrepID query, for example *-Commissioning2018-ZeroBias-*">
        </v-card-text>
        <small style="opacity: 0.4">Note: for performance reasons query result is limited to 1000 PrepIDs</small>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn small class="mr-1 mb-1" color="primary" v-if="!listLength(editableObject.input)" :disabled="!getRequestsDialog.input.length" @click="getRequests(true)">Fetch</v-btn>
          <v-btn small class="mr-1 mb-1" color="primary" v-if="listLength(editableObject.input)" :disabled="!getRequestsDialog.input.length" @click="getRequests(true)" title="Fetch list and replace existing list with newly fetched one">Fetch and replace</v-btn>
          <v-btn small class="mr-1 mb-1" color="primary" v-if="listLength(editableObject.input)" :disabled="!getRequestsDialog.input.length" @click="getRequests(false)" title="Fetch list and append it to an existing list">Fetch and append</v-btn>
          <v-btn small class="mr-1 mb-1" color="error" @click="closeGetRequestsDialog()">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <LoadingOverlay :visible="loading"/>
    <v-dialog v-model="errorDialog.visible"
              max-width="50%">
      <v-card>
        <v-card-title class="headline">
          {{errorDialog.title}}
        </v-card-title>
        <v-card-text>
          <span v-html="errorDialog.description"></span>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn small class="mr-1 mb-1" color="primary" @click="clearErrorDialog()">
            Dismiss
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>

import axios from 'axios'
import { utilsMixin } from '../mixins/UtilsMixin.js'
import LoadingOverlay from './LoadingOverlay.vue'
import Autocompleter from './Autocompleter.vue'
import JSONField from './JSONField.vue'

export default {
  name: 'TicketsEdit',
  components: {
    LoadingOverlay,
    Autocompleter,
    JSONField
  },
  mixins: [
    utilsMixin
  ],
  data () {
    return {
      prepid: undefined,
      editableObject: {},
      editingInfo: {},
      showJobDictOverwrite: false,
      loading: true,
      creatingNew: true,
      errorDialog: {
        visible: false,
        title: '',
        description: '',
      },
      getDatasetsDialog: {
        visible: false,
        input: '',
        exclude: 'validation,pilot',
      },
      getRequestsDialog: {
        visible: false,
        input: '',
      }
    }
  },
  created () {
    let query = Object.assign({}, this.$route.query);
    if (query.prepid && query.prepid.length) {
      this.prepid = query.prepid;
    } else {
      this.prepid = '';
    }
    this.creatingNew = this.prepid.length == 0;
    this.loading = true;
    let component = this;
    axios.get('api/tickets/get_editable/' + this.prepid).then(response => {
      let objectInfo = response.data.response.object;
      let editingInfo = response.data.response.editing_info;
      if (query.clone && query.clone.length) {
        axios.get('api/tickets/get_editable/' + query.clone).then(templateResponse => {
          let templateInfo = templateResponse.data.response.object;
          let templateEditingInfo = templateResponse.data.response.editing_info;
          templateInfo.prepid = objectInfo.prepid;
          templateInfo.history = objectInfo.history;
          templateInfo.status = objectInfo.status;
          templateInfo.created_requests = objectInfo.created_requests;
          for (let i = 0; i < templateEditingInfo.steps.length; i++) {
            editingInfo.steps.push({'subcampaign': true,
                                    'processing_string': true,
                                    'priority': true,
                                    'size_per_event': true,
                                    'time_per_event': true})
          }
          templateInfo.input = templateInfo.input.filter(Boolean).join('\n');
          component.editableObject = templateInfo;
          component.editingInfo = editingInfo;
          component.showJobDictOverwrite = Object.keys(component.editableObject.job_dict_overwrite) != 0;
          component.loading = false;
        }).catch(error => {
          component.loading = false;
          component.showError('Error fetching editing information', component.getError(error));
        });
      } else {
        if (query.input_requests && query.input_requests.length) {
          objectInfo.input = query.input_requests.split(',').filter(Boolean).join('\n');
        } else {
          objectInfo.input = objectInfo.input.filter(Boolean).join('\n');
        }
        component.editableObject = objectInfo;
        component.editingInfo = editingInfo;
        component.showJobDictOverwrite = Object.keys(component.editableObject.job_dict_overwrite) != 0;
        if (component.creatingNew) {
          component.addStep();
        }
        component.loading = false;
      }
    }).catch(error => {
      component.loading = false;
      component.showError('Error fetching editing information', component.getError(error));
    });
  },
  methods: {
    save: function() {
      this.loading = true;
      let editableObject = this.makeCopy(this.editableObject);
      editableObject.notes = editableObject.notes.trim();
      editableObject.input = editableObject.input.split('\n').map(function(s) { return s.trim() }).filter(Boolean);
      let httpRequest;
      if (this.creatingNew) {
        httpRequest = axios.put('api/tickets/create', editableObject);
      } else {
        httpRequest = axios.post('api/tickets/update', editableObject);
      }
      let component = this;
      httpRequest.then(response => {
        component.loading = false;
        window.location = 'tickets?prepid=' + response.data.response.prepid;
      }).catch(error => {
        component.loading = false;
        this.showError('Error saving ticket', component.getError(error));
      });
    },
    getSubcampaign: function(stepIdentifier, subcampaignName) {
      let stepIndex = parseInt(stepIdentifier.replace('Step', ''));
      let component = this;
      let step = this.editableObject.steps[stepIndex]
      let url = 'api/subcampaigns/get/' + subcampaignName;
      // Timeout 120000ms is 2 minutes
      this.loading = true;
      let httpRequest = axios.get(url, {timeout: 120000});
      httpRequest.then(response => {
        component.loading = false;
        let sequencesLength = response.data.response.sequences.length;
        component.$set(step, 'size_per_event', Array(sequencesLength).fill(1.0));
        component.$set(step, 'time_per_event', Array(sequencesLength).fill(1.0));
      }).catch(() => {
        component.loading = false;
        component.$set(step, 'size_per_event', []);
        component.$set(step, 'time_per_event', []);
      });
    },
    getDatasets: function(replace) {
      this.loading = true;
      let component = this;
      let url = 'api/tickets/get_datasets?q=' + this.getDatasetsDialog.input;
      let exclude = this.cleanSplit(this.getDatasetsDialog.exclude);
      if (exclude.length) {
        url += '&exclude=' + exclude.join(',');
      }
      // Timeout 120000ms is 2 minutes
      let httpRequest = axios.get(url, {timeout: 120000});
      this.closeGetDatasetsDialog();
      httpRequest.then(response => {
        if (replace) {
          component.editableObject.input = response.data.response.filter(Boolean).join('\n');
        } else {
          let existingItems = component.cleanSplit(component.editableObject.input);
          for (let item of response.data.response.filter(Boolean)) {
            if (!existingItems.includes(item)) {
              existingItems.push(item);
            }
          }
          component.editableObject.input = existingItems.join('\n');
        }
        component.loading = false;
      }).catch(error => {
        component.loading = false;
        this.showError('Error getting datasets for ticket', component.getError(error))
      });
    },
    showGetDatasetsDialog: function() {
      this.getDatasetsDialog.visible = true;
      this.getDatasetsDialog.input = '';
    },
    closeGetDatasetsDialog: function() {
      this.getDatasetsDialog.visible = false;
      this.getDatasetsDialog.input = '';
    },
    getRequests: function(replace) {
      this.loading = true;
      let component = this;
      let url = 'api/tickets/get_requests?q=' + this.getRequestsDialog.input;
      // Timeout 120000ms is 2 minutes
      let httpRequest = axios.get(url, {timeout: 120000});
      this.closeGetRequestsDialog();
      httpRequest.then(response => {
        if (replace) {
          component.editableObject.input = response.data.response.filter(Boolean).join('\n');
        } else {
          let existingItems = component.cleanSplit(component.editableObject.input);
          for (let item of response.data.response.filter(Boolean)) {
            if (!existingItems.includes(item)) {
              existingItems.push(item);
            }
          }
          component.editableObject.input = existingItems.join('\n');
        }
        component.loading = false;
      }).catch(error => {
        component.loading = false;
        this.showError('Error getting datasets for ticket', component.getError(error))
      });
    },
    showGetRequestsDialog: function() {
      this.getRequestsDialog.visible = true;
      this.getRequestsDialog.input = '';
    },
    closeGetRequestsDialog: function() {
      this.getRequestsDialog.visible = false;
      this.getRequestsDialog.input = '';
    },
    addStep: function() {
      this.editableObject.steps.push({'subcampaign': '',
                                      'processing_string': '',
                                      'priority': 110000,
                                      'size_per_event': [],
                                      'time_per_event': []});
      this.editingInfo.steps.push({'subcampaign': true,
                                   'processing_string': true,
                                   'priority': true,
                                   'size_per_event': true,
                                   'time_per_event': true});
      if (this.editableObject.steps.length > 1) {
        // Copy processing string of last step
        const steps = this.editableObject.steps;
        steps[steps.length - 1]['processing_string'] = steps[steps.length - 2]['processing_string'];
        steps[steps.length - 1]['priority'] = steps[steps.length - 2]['priority'];
      }
    },
    deleteStep: function(index) {
      this.editableObject.steps.splice(index, 1);
      this.editingInfo.steps.splice(index, 1);
    },
    clearErrorDialog: function() {
      this.errorDialog.visible = false;
      this.errorDialog.title = '';
      this.errorDialog.description = '';
    },
    showError: function(title, description) {
      this.clearErrorDialog();
      this.errorDialog.title = title;
      this.errorDialog.description = description;
      this.errorDialog.visible = true;
    },
    getSubcampaignSuggestions: function(stepIdentifier, value, callback) {
      if (!value || value.length == 0) {
        callback([]);
      }
      axios.get('api/suggestions?db_name=subcampaigns&query=' + value).then(response => {
        callback(response.data.response);
      }).catch(() => {
        callback([]);
      });
    },
    cancel: function() {
      if (this.creatingNew) {
        window.location = 'subcampaigns';
      } else {
        window.location = 'subcampaigns?prepid=' + this.prepid;
      }
    },
    toggleJobDictOverwrite: function() {
      if (this.showJobDictOverwrite) {
        this.showJobDictOverwrite = false;
        return;
      }
      const component = this;
      if (confirm('Are you sure you know what you are doing? This is a very dangerous action!')) {
        component.showJobDictOverwrite = true;
      }
    },
  }
}
</script>

<style>
.show-job-dict-overwrite {
  color: var(--v-anchor-base);
  cursor: pointer;
}
.show-job-dict-overwrite:hover {
  color: red;
  font-weight: 700;
}
</style>