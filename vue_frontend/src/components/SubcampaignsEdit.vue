<template>
  <div>
    <h1 class="page-title" v-if="creatingNew"><span class="font-weight-light">Creating</span> new subcampaign</h1>
    <h1 class="page-title" v-else><span class="font-weight-light">Editing subcampaign</span> {{prepid}}</h1>
    <v-card raised class="page-card">
      <table v-if="editableObject">
        <tr>
          <td>PrepID</td>
          <td><input type="text" v-model="editableObject.prepid" :disabled="!editingInfo.prepid"></td>
        </tr>
        <tr>
          <td>CMSSW release</td>
          <td><input type="text" v-model="editableObject.cmssw_release" :disabled="!editingInfo.cmssw_release"></td>
        </tr>
        <tr>
          <td>Enable harvesting</td>
          <td><input type="checkbox" v-model="editableObject.enable_harvesting" :disabled="!editingInfo.enable_harvesting || !hasStep(editableObject, 'DQM')"/></td>
        </tr>
        <tr>
          <td>Energy</td>
          <td><input type="number" min="0" v-model="editableObject.energy" :disabled="!editingInfo.energy">TeV</td>
        </tr>
        <tr>
          <td>Memory</td>
          <td><input type="number" v-model="editableObject.memory" :disabled="!editingInfo.memory">MB</td>
        </tr>
        <tr>
          <td>Notes</td>
          <td><textarea v-model="editableObject.notes" :disabled="!editingInfo.notes"></textarea></td>
        </tr>
        <tr>
          <td>Runs JSON</td>
          <td>
            <input type="text" v-model="editableObject.runs_json_path" :disabled="!editingInfo.runs_json_path" placeholder="Example: Collisions16/13TeV/DCSOnly/json_DCSONLY.txt">
            <br>
            <small>Path in <a href="https://cms-service-dqmdc.web.cern.ch/CAF/certification/" target="_blank">here</a>, e.g. "Collisions16/13TeV/DCSOnly/json_DCSONLY.txt"</small>
          </td>
        </tr>
        <tr>
          <td>Sequences ({{listLength(editableObject.sequences)}})</td>
          <td>
            <div v-for="(sequence, index) in editableObject.sequences" :key="index">
              <h3>Sequence {{index + 1}}</h3>
              <table>
                <tr>
                  <td>--conditions</td><td><input type="text" v-model="sequence.conditions" :disabled="!editableObject.sequences"></td>
                </tr>
                <tr>
                  <td>--customise</td><td><input type="text" v-model="sequence.customise" :disabled="!editableObject.sequences"></td>
                </tr>
                <tr>
                  <td>--datatier</td><td><input type="text" v-model="sequence.datatier" :disabled="!editableObject.sequences"></td>
                </tr>
                <tr>
                  <td>--era</td><td><input type="text" v-model="sequence.era" :disabled="!editableObject.sequences"></td>
                </tr>
                <tr>
                  <td>--eventcontent</td><td><input type="text" v-model="sequence.eventcontent" :disabled="!editableObject.sequences"></td>
                </tr>
                <tr>
                  <td>--extra</td><td><input type="text" v-model="sequence.extra" :disabled="!editableObject.sequences"></td>
                </tr>
                <tr>
                  <td>--nThreads</td><td><input type="number" min="1" v-model="sequence.nThreads" :disabled="!editableObject.sequences"></td>
                </tr>
                <tr>
                  <td>--scenario</td>
                  <td>
                    <select v-model="sequence.scenario" :disabled="!editableObject.sequences">
                      <option>pp</option>
                      <option>cosmics</option>
                      <option>nocoll</option>
                      <option>HeavyIons</option>
                    </select>
                  </td>
                </tr>
                <tr>
                  <td>--step</td><td><input type="text" v-model="sequence.step" :disabled="!editableObject.sequences"></td>
                </tr>
                <tr>
                  <td>GPU</td>
                  <td>
                    <select v-model="sequence.gpu.requires" :disabled="!editingInfo.sequences">
                      <option>forbidden</option>
                      <option>optional</option>
                      <option>required</option>
                    </select>
                  </td>
                </tr>
                <tr v-if="sequence.gpu.requires != 'forbidden'">
                  <td>GPU parameters</td>
                  <td>
                    <table>
                      <tr>
                        <td>GPU memory</td>
                        <td><input type="number" v-model="sequence.gpu.gpu_memory" :disabled="!editingInfo.sequences" min="0" max="32000" step="1000">MB</td>
                      </tr>
                      <tr>
                        <td>CUDA capabilities</td>
                        <td><input type="text" v-model="sequence.gpu.cuda_capabilities" placeholder="E.g. 6.0,6.1,6.2" :disabled="!editingInfo.sequences"></td>
                      </tr>
                      <tr>
                        <td>CUDA runtime</td>
                        <td><input type="text" v-model="sequence.gpu.cuda_runtime" :disabled="!editingInfo.sequences"></td>
                      </tr>
                      <tr>
                        <td>GPU name</td>
                        <td><input type="text" v-model="sequence.gpu.gpu_name" :disabled="!editingInfo.sequences"></td>
                      </tr>
                      <tr>
                        <td>CUDA driver version</td>
                        <td><input type="text" v-model="sequence.gpu.cuda_driver_version" :disabled="!editingInfo.sequences"></td>
                      </tr>
                      <tr>
                        <td>CUDA runtime version</td>
                        <td><input type="text" v-model="sequence.gpu.cuda_runtime_version" :disabled="!editingInfo.sequences"></td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
              <v-btn small
                     class="mr-1 mb-1"
                     color="error"
                     v-if="editingInfo.sequences"
                     @click="deleteSequence(index)">Delete sequence {{index + 1}}</v-btn>
              <hr>
            </div>
            <v-btn small
                   class="mr-1 mb-1 mt-1"
                   color="primary"
                   v-if="editingInfo.sequences && editableObject.sequences.length < 5"
                   @click="addSequence()">Add sequence {{listLength(editableObject.sequences) + 1}}</v-btn>
          </td>
        </tr>
      </table>
      <v-btn small class="mr-1 mt-1" color="primary" @click="save()">Save</v-btn>
      <v-btn small class="mr-1 mt-1" color="error" @click="cancel()">Cancel</v-btn>
    </v-card>
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

export default {
  mixins: [
    utilsMixin
  ],
  components: {
    LoadingOverlay
  },
  data () {
    return {
      prepid: undefined,
      editableObject: {},
      editingInfo: {},
      loading: true,
      creatingNew: true,
      errorDialog: {
        visible: false,
        title: '',
        description: '',
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
    axios.get('api/subcampaigns/get_editable/' + this.prepid).then(response => {
      let objectInfo = response.data.response.object;
      let editingInfo = response.data.response.editing_info;
      if (query.clone && query.clone.length) {
        axios.get('api/subcampaigns/get_editable/' + query.clone).then(templateResponse => {
          let templateInfo = templateResponse.data.response.object;
          templateInfo.prepid = objectInfo.prepid;
          templateInfo.history = objectInfo.history;
          component.editableObject = templateInfo;
          component.editingInfo = editingInfo;
          component.loading = false;
        }).catch(error => {
          component.loading = false;
          component.showError('Error fetching editing information', component.getError(error));
        });
      } else {
        component.editableObject = objectInfo;
        component.editingInfo = editingInfo;
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
      let httpRequest;
      if (this.creatingNew) {
        httpRequest = axios.put('api/subcampaigns/create', editableObject);
      } else {
        httpRequest = axios.post('api/subcampaigns/update', editableObject);
      }
      let component = this;
      httpRequest.then(response => {
        component.loading = false;
        window.location = 'subcampaigns?prepid=' + response.data.response.prepid;
      }).catch(error => {
        component.loading = false;
        this.showError('Error saving subcampaign', component.getError(error));
      });
    },
    addSequence: function() {
      this.loading = true;
      let component = this;
      axios.get('api/subcampaigns/get_default_sequence/' + (this.creatingNew ? '' : this.prepid)).then(response => {
        component.editableObject.sequences.push(response.data.response);
        component.loading = false;
      }).catch(error => {
        component.loading = false;
        this.showError('Error getting sequence information', component.getError(error));
      });
    },
    deleteSequence: function(index) {
      this.editableObject.sequences.splice(index, 1);
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
    cancel: function() {
      if (this.creatingNew) {
        window.location = 'subcampaigns';
      } else {
        window.location = 'subcampaigns?prepid=' + this.prepid;
      }
    },
  }
}
</script>
