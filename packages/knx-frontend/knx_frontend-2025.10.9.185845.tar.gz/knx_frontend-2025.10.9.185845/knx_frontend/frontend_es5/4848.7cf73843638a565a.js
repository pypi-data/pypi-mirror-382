"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["4848"],{79080:function(t,e,i){i.a(t,(async function(t,e){try{i(35748),i(5934),i(95013);var a=i(69868),s=i(90227),n=i(84922),o=i(11991),r=i(73120),l=i(83566),d=i(84810),p=i(72698),h=i(5503),c=i(76943),u=(i(23749),t([d,c]));[d,c]=u.then?(await u)():u;let _,g,v,m,y,w,f=t=>t;const b=t=>{if("object"!=typeof t||null===t)return!1;for(const e in t)if(Object.prototype.hasOwnProperty.call(t,e))return!1;return!0};class $ extends n.WF{setValue(t){try{this._yaml=b(t)?"":(0,s.Bh)(t,{schema:this.yamlSchema,quotingType:'"',noRefs:!0})}catch(e){console.error(e,t),alert(`There was an error converting to YAML: ${e}`)}}firstUpdated(){void 0!==this.defaultValue&&this.setValue(this.defaultValue)}willUpdate(t){super.willUpdate(t),this.autoUpdate&&t.has("value")&&this.setValue(this.value)}focus(){var t,e;null!==(t=this._codeEditor)&&void 0!==t&&t.codemirror&&(null===(e=this._codeEditor)||void 0===e||e.codemirror.focus())}render(){return void 0===this._yaml?n.s6:(0,n.qy)(_||(_=f`
      ${0}
      <ha-code-editor
        .hass=${0}
        .value=${0}
        .readOnly=${0}
        .disableFullscreen=${0}
        mode="yaml"
        autocomplete-entities
        autocomplete-icons
        .error=${0}
        @value-changed=${0}
        @blur=${0}
        dir="ltr"
      ></ha-code-editor>
      ${0}
      ${0}
    `),this.label?(0,n.qy)(g||(g=f`<p>${0}${0}</p>`),this.label,this.required?" *":""):n.s6,this.hass,this._yaml,this.readOnly,this.disableFullscreen,!1===this.isValid,this._onChange,this._onBlur,this._showingError?(0,n.qy)(v||(v=f`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):n.s6,this.copyClipboard||this.hasExtraActions?(0,n.qy)(m||(m=f`
            <div class="card-actions">
              ${0}
              <slot name="extra-actions"></slot>
            </div>
          `),this.copyClipboard?(0,n.qy)(y||(y=f`
                    <ha-button appearance="plain" @click=${0}>
                      ${0}
                    </ha-button>
                  `),this._copyYaml,this.hass.localize("ui.components.yaml-editor.copy_to_clipboard")):n.s6):n.s6)}_onChange(t){let e;t.stopPropagation(),this._yaml=t.detail.value;let i,a=!0;if(this._yaml)try{e=(0,s.Hh)(this._yaml,{schema:this.yamlSchema})}catch(n){a=!1,i=`${this.hass.localize("ui.components.yaml-editor.error",{reason:n.reason})}${n.mark?` (${this.hass.localize("ui.components.yaml-editor.error_location",{line:n.mark.line+1,column:n.mark.column+1})})`:""}`}else e={};this._error=null!=i?i:"",a&&(this._showingError=!1),this.value=e,this.isValid=a,(0,r.r)(this,"value-changed",{value:e,isValid:a,errorMsg:i})}_onBlur(){this.showErrors&&this._error&&(this._showingError=!0)}get yaml(){return this._yaml}async _copyYaml(){this.yaml&&(await(0,h.l)(this.yaml),(0,p.P)(this,{message:this.hass.localize("ui.common.copied_clipboard")}))}static get styles(){return[l.RF,(0,n.AH)(w||(w=f`
        .card-actions {
          border-radius: var(
            --actions-border-radius,
            0px 0px var(--ha-card-border-radius, 12px)
              var(--ha-card-border-radius, 12px)
          );
          border: 1px solid var(--divider-color);
          padding: 5px 16px;
        }
        ha-code-editor {
          flex-grow: 1;
          min-height: 0;
        }
      `))]}constructor(...t){super(...t),this.yamlSchema=s.my,this.isValid=!0,this.autoUpdate=!1,this.readOnly=!1,this.disableFullscreen=!1,this.required=!1,this.copyClipboard=!1,this.hasExtraActions=!1,this.showErrors=!0,this._yaml="",this._error="",this._showingError=!1}}(0,a.__decorate)([(0,o.MZ)({attribute:!1})],$.prototype,"hass",void 0),(0,a.__decorate)([(0,o.MZ)()],$.prototype,"value",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],$.prototype,"yamlSchema",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],$.prototype,"defaultValue",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:"is-valid",type:Boolean})],$.prototype,"isValid",void 0),(0,a.__decorate)([(0,o.MZ)()],$.prototype,"label",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:"auto-update",type:Boolean})],$.prototype,"autoUpdate",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:"read-only",type:Boolean})],$.prototype,"readOnly",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean,attribute:"disable-fullscreen"})],$.prototype,"disableFullscreen",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],$.prototype,"required",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:"copy-clipboard",type:Boolean})],$.prototype,"copyClipboard",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:"has-extra-actions",type:Boolean})],$.prototype,"hasExtraActions",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:"show-errors",type:Boolean})],$.prototype,"showErrors",void 0),(0,a.__decorate)([(0,o.wk)()],$.prototype,"_yaml",void 0),(0,a.__decorate)([(0,o.wk)()],$.prototype,"_error",void 0),(0,a.__decorate)([(0,o.wk)()],$.prototype,"_showingError",void 0),(0,a.__decorate)([(0,o.P)("ha-code-editor")],$.prototype,"_codeEditor",void 0),$=(0,a.__decorate)([(0,o.EM)("ha-yaml-editor")],$),e()}catch(_){e(_)}}))},4204:function(t,e,i){i.d(e,{a:function(){return n}});i(35748),i(5934),i(95013);var a=i(73120);const s=()=>i.e("2747").then(i.bind(i,55910)),n=(t,e)=>{(0,a.r)(t,"show-dialog",{addHistory:!1,dialogTag:"dialog-tts-try",dialogImport:s,dialogParams:e})}},47474:function(t,e,i){i(35748),i(5934),i(95013);var a=i(69868),s=i(84922),n=i(11991),o=i(65940);i(75518);let r,l,d=t=>t;class p extends s.WF{async focus(){var t;await this.updateComplete;const e=null===(t=this.renderRoot)||void 0===t?void 0:t.querySelector("ha-form");null==e||e.focus()}render(){return(0,s.qy)(r||(r=d`
      <div class="section">
        <div class="intro">
          <h3>
            ${0}
          </h3>
          <p>
            ${0}
          </p>
        </div>
        <ha-form
          .schema=${0}
          .data=${0}
          .hass=${0}
          .computeLabel=${0}
        ></ha-form>
      </div>
    `),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.config.title"),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.config.description"),this._schema(this.supportedLanguages),this.data,this.hass,this._computeLabel)}constructor(...t){super(...t),this._schema=(0,o.A)((t=>[{name:"",type:"grid",schema:[{name:"name",required:!0,selector:{text:{}}},t?{name:"language",required:!0,selector:{language:{languages:t}}}:{name:"",type:"constant"}]}])),this._computeLabel=t=>t.name?this.hass.localize(`ui.panel.config.voice_assistants.assistants.pipeline.detail.form.${t.name}`):""}}p.styles=(0,s.AH)(l||(l=d`
    .section {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      box-sizing: border-box;
      padding: 16px;
    }
    .intro {
      margin-bottom: 16px;
    }
    h3 {
      font-size: var(--ha-font-size-xl);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-condensed);
      margin-top: 0;
      margin-bottom: 4px;
    }
    p {
      color: var(--secondary-text-color);
      font-size: var(--mdc-typography-body2-font-size, var(--ha-font-size-s));
      margin-top: 0;
      margin-bottom: 0;
    }
  `)),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"data",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1,type:Array})],p.prototype,"supportedLanguages",void 0),p=(0,a.__decorate)([(0,n.EM)("assist-pipeline-detail-config")],p)},75787:function(t,e,i){i(35748),i(99342),i(12977),i(95013);var a=i(69868),s=i(84922),n=i(11991),o=i(65940),r=(i(75518),i(73120));let l,d,p=t=>t;class h extends s.WF{render(){var t,e;return(0,s.qy)(l||(l=p`
      <div class="section">
        <div class="intro">
          <h3>
            ${0}
          </h3>
          <p>
            ${0}
          </p>
        </div>
        <ha-form
          .schema=${0}
          .data=${0}
          .hass=${0}
          .computeLabel=${0}
          .computeHelper=${0}
          @supported-languages-changed=${0}
        ></ha-form>
      </div>
    `),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.conversation.title"),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.conversation.description"),this._schema(null===(t=this.data)||void 0===t?void 0:t.conversation_engine,null===(e=this.data)||void 0===e?void 0:e.language,this._supportedLanguages),this.data,this.hass,this._computeLabel,this._computeHelper,this._supportedLanguagesChanged)}_supportedLanguagesChanged(t){"*"===t.detail.value&&setTimeout((()=>{const t=Object.assign({},this.data);t.conversation_language="*",(0,r.r)(this,"value-changed",{value:t})}),0),this._supportedLanguages=t.detail.value}constructor(...t){super(...t),this._schema=(0,o.A)(((t,e,i)=>{const a=[{name:"",type:"grid",schema:[{name:"conversation_engine",required:!0,selector:{conversation_agent:{language:e}}}]}];return"*"!==i&&null!=i&&i.length&&a[0].schema.push({name:"conversation_language",required:!0,selector:{language:{languages:i,no_sort:!0}}}),"conversation.home_assistant"!==t&&a.push({name:"prefer_local_intents",default:!0,selector:{boolean:{}}}),a})),this._computeLabel=t=>t.name?this.hass.localize(`ui.panel.config.voice_assistants.assistants.pipeline.detail.form.${t.name}`):"",this._computeHelper=t=>t.name?this.hass.localize(`ui.panel.config.voice_assistants.assistants.pipeline.detail.form.${t.name}_description`):""}}h.styles=(0,s.AH)(d||(d=p`
    .section {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      box-sizing: border-box;
      padding: 16px;
    }
    .intro {
      margin-bottom: 16px;
    }
    h3 {
      font-size: var(--ha-font-size-xl);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-condensed);
      margin-top: 0;
      margin-bottom: 4px;
    }
    p {
      color: var(--secondary-text-color);
      font-size: var(--mdc-typography-body2-font-size, var(--ha-font-size-s));
      margin-top: 0;
      margin-bottom: 0;
    }
  `)),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],h.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],h.prototype,"data",void 0),(0,a.__decorate)([(0,n.wk)()],h.prototype,"_supportedLanguages",void 0),h=(0,a.__decorate)([(0,n.EM)("assist-pipeline-detail-conversation")],h)},1783:function(t,e,i){i(35748),i(95013);var a=i(69868),s=i(84922),n=i(11991),o=i(65940);i(75518);let r,l,d=t=>t;class p extends s.WF{render(){var t;return(0,s.qy)(r||(r=d`
      <div class="section">
        <div class="intro">
          <h3>
            ${0}
          </h3>
          <p>
            ${0}
          </p>
        </div>
        <ha-form
          .schema=${0}
          .data=${0}
          .hass=${0}
          .computeLabel=${0}
          @supported-languages-changed=${0}
        ></ha-form>
      </div>
    `),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.stt.title"),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.stt.description"),this._schema(null===(t=this.data)||void 0===t?void 0:t.language,this._supportedLanguages),this.data,this.hass,this._computeLabel,this._supportedLanguagesChanged)}_supportedLanguagesChanged(t){this._supportedLanguages=t.detail.value}constructor(...t){super(...t),this._schema=(0,o.A)(((t,e)=>[{name:"",type:"grid",schema:[{name:"stt_engine",selector:{stt:{language:t}}},null!=e&&e.length?{name:"stt_language",required:!0,selector:{language:{languages:e,no_sort:!0}}}:{name:"",type:"constant"}]}])),this._computeLabel=t=>t.name?this.hass.localize(`ui.panel.config.voice_assistants.assistants.pipeline.detail.form.${t.name}`):""}}p.styles=(0,s.AH)(l||(l=d`
    .section {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      box-sizing: border-box;
      padding: 16px;
    }
    .intro {
      margin-bottom: 16px;
    }
    h3 {
      font-size: var(--ha-font-size-xl);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-condensed);
      margin-top: 0;
      margin-bottom: 4px;
    }
    p {
      color: var(--secondary-text-color);
      font-size: var(--mdc-typography-body2-font-size, var(--ha-font-size-s));
      margin-top: 0;
      margin-bottom: 0;
    }
  `)),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"data",void 0),(0,a.__decorate)([(0,n.wk)()],p.prototype,"_supportedLanguages",void 0),p=(0,a.__decorate)([(0,n.EM)("assist-pipeline-detail-stt")],p)},53751:function(t,e,i){i.a(t,(async function(t,e){try{i(35748),i(5934),i(95013);var a=i(69868),s=i(84922),n=i(11991),o=i(65940),r=i(76943),l=(i(75518),i(4204)),d=t([r]);r=(d.then?(await d)():d)[0];let p,h,c,u=t=>t;class _ extends s.WF{render(){var t,e;return(0,s.qy)(p||(p=u`
      <div class="section">
        <div class="content">
          <div class="intro">
          <h3>
            ${0}
          </h3>
          <p>
            ${0}
          </p>
          </div>
          <ha-form
            .schema=${0}
            .data=${0}
            .hass=${0}
            .computeLabel=${0}
            @supported-languages-changed=${0}
          ></ha-form>
        </div>

       ${0}
        </div>
      </div>
    `),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.tts.title"),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.tts.description"),this._schema(null===(t=this.data)||void 0===t?void 0:t.language,this._supportedLanguages),this.data,this.hass,this._computeLabel,this._supportedLanguagesChanged,null!==(e=this.data)&&void 0!==e&&e.tts_engine?(0,s.qy)(h||(h=u`<div class="footer">
               <ha-button @click=${0}>
                 ${0}
               </ha-button>
             </div>`),this._preview,this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.try_tts")):s.s6)}async _preview(){if(!this.data)return;const t=this.data.tts_engine,e=this.data.tts_language||void 0,i=this.data.tts_voice||void 0;t&&(0,l.a)(this,{engine:t,language:e,voice:i})}_supportedLanguagesChanged(t){this._supportedLanguages=t.detail.value}constructor(...t){super(...t),this._schema=(0,o.A)(((t,e)=>[{name:"",type:"grid",schema:[{name:"tts_engine",selector:{tts:{language:t}}},null!=e&&e.length?{name:"tts_language",required:!0,selector:{language:{languages:e,no_sort:!0}}}:{name:"",type:"constant"},{name:"tts_voice",selector:{tts_voice:{}},context:{language:"tts_language",engineId:"tts_engine"},required:!0}]}])),this._computeLabel=t=>t.name?this.hass.localize(`ui.panel.config.voice_assistants.assistants.pipeline.detail.form.${t.name}`):""}}_.styles=(0,s.AH)(c||(c=u`
    .section {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
    }
    .content {
      padding: 16px;
    }
    .intro {
      margin-bottom: 16px;
    }
    h3 {
      font-size: var(--ha-font-size-xl);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-condensed);
      margin-top: 0;
      margin-bottom: 4px;
    }
    p {
      color: var(--secondary-text-color);
      font-size: var(--mdc-typography-body2-font-size, var(--ha-font-size-s));
      margin-top: 0;
      margin-bottom: 0;
    }
    .footer {
      border-top: 1px solid var(--divider-color);
      padding: 8px 16px;
    }
  `)),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],_.prototype,"data",void 0),(0,a.__decorate)([(0,n.wk)()],_.prototype,"_supportedLanguages",void 0),_=(0,a.__decorate)([(0,n.EM)("assist-pipeline-detail-tts")],_),e()}catch(p){e(p)}}))},54641:function(t,e,i){i(35748),i(65315),i(37089),i(59023),i(12977),i(5934),i(95013);var a=i(69868),s=i(84922),n=i(11991),o=i(65940);i(75518);var r=i(73120);let l,d,p=t=>t;class h extends s.WF{willUpdate(t){var e,i,a,s;t.has("data")&&(null===(e=t.get("data"))||void 0===e?void 0:e.wake_word_entity)!==(null===(i=this.data)||void 0===i?void 0:i.wake_word_entity)&&(null!==(a=t.get("data"))&&void 0!==a&&a.wake_word_entity&&null!==(s=this.data)&&void 0!==s&&s.wake_word_id&&(0,r.r)(this,"value-changed",{value:Object.assign(Object.assign({},this.data),{},{wake_word_id:void 0})}),this._fetchWakeWords())}render(){return(0,s.qy)(l||(l=p`
      <div class="section">
        <div class="content">
          <div class="intro">
            <h3>
              ${0}
            </h3>
            <p>
              ${0}
            </p>
            <ha-alert alert-type="info">
              ${0}
            </ha-alert>
          </div>
          <ha-form
            .schema=${0}
            .data=${0}
            .hass=${0}
            .computeLabel=${0}
          ></ha-form>
        </div>
      </div>
    `),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.wakeword.title"),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.wakeword.description"),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.wakeword.note"),this._schema(this._wakeWords),this.data,this.hass,this._computeLabel)}async _fetchWakeWords(){var t,e;if(this._wakeWords=void 0,null===(t=this.data)||void 0===t||!t.wake_word_entity)return;const i=this.data.wake_word_entity,a=await(s=this.hass,n=i,s.callWS({type:"wake_word/info",entity_id:n}));var s,n,o;this.data.wake_word_entity===i&&(this._wakeWords=a.wake_words,!this.data||null!==(e=this.data)&&void 0!==e&&e.wake_word_id&&this._wakeWords.some((t=>t.id===this.data.wake_word_id))||(0,r.r)(this,"value-changed",{value:Object.assign(Object.assign({},this.data),{},{wake_word_id:null===(o=this._wakeWords[0])||void 0===o?void 0:o.id})}))}constructor(...t){super(...t),this._schema=(0,o.A)((t=>[{name:"",type:"grid",schema:[{name:"wake_word_entity",selector:{entity:{domain:"wake_word"}}},null!=t&&t.length?{name:"wake_word_id",required:!0,selector:{select:{mode:"dropdown",sort:!0,options:t.map((t=>({value:t.id,label:t.name})))}}}:{name:"",type:"constant"}]}])),this._computeLabel=t=>t.name?this.hass.localize(`ui.panel.config.voice_assistants.assistants.pipeline.detail.form.${t.name}`):""}}h.styles=(0,s.AH)(d||(d=p`
    .section {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
    }
    .content {
      padding: 16px;
    }
    .intro {
      margin-bottom: 16px;
    }
    h3 {
      font-size: var(--ha-font-size-xl);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-condensed);
      margin-top: 0;
      margin-bottom: 4px;
    }
    p {
      color: var(--secondary-text-color);
      font-size: var(--mdc-typography-body2-font-size, var(--ha-font-size-s));
      margin-top: 0;
      margin-bottom: 0;
    }
    a {
      color: var(--primary-color);
    }
  `)),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],h.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],h.prototype,"data",void 0),(0,a.__decorate)([(0,n.wk)()],h.prototype,"_wakeWords",void 0),h=(0,a.__decorate)([(0,n.EM)("assist-pipeline-detail-wakeword")],h)},55485:function(t,e,i){i.a(t,(async function(t,e){try{i(35748),i(65315),i(22416),i(36874),i(95013);var a=i(69868),s=i(84922),n=i(11991),o=i(65940),r=i(85023),l=i(10507),d=t([l]);l=(d.then?(await d)():d)[0];let p,h,c,u=t=>t;class _ extends s.WF{render(){const t=this._processEvents(this.events);return t?(0,s.qy)(c||(c=u`
      <assist-render-pipeline-run
        .hass=${0}
        .pipelineRun=${0}
      ></assist-render-pipeline-run>
    `),this.hass,t):this.events.length?(0,s.qy)(p||(p=u`<ha-alert alert-type="error">Error showing run</ha-alert>
          <ha-card>
            <ha-expansion-panel>
              <span slot="header">Raw</span>
              <pre>${0}</pre>
            </ha-expansion-panel>
          </ha-card>`),JSON.stringify(this.events,null,2)):(0,s.qy)(h||(h=u`<ha-alert alert-type="warning"
        >There were no events in this run.</ha-alert
      >`))}constructor(...t){super(...t),this._processEvents=(0,o.A)((t=>{let e;return t.forEach((t=>{e=(0,r.QC)(e,t)})),e}))}}(0,a.__decorate)([(0,n.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],_.prototype,"events",void 0),_=(0,a.__decorate)([(0,n.EM)("assist-render-pipeline-events")],_),e()}catch(p){e(p)}}))},10507:function(t,e,i){i.a(t,(async function(t,e){try{i(35748),i(99342),i(65315),i(84136),i(37089),i(95013);var a=i(69868),s=i(84922),n=i(11991),o=(i(86853),i(23749),i(76943)),r=i(71622),l=(i(99741),i(44665)),d=i(79080),p=i(47420),h=t([o,r,d,l]);[o,r,d,l]=h.then?(await h)():h;let c,u,_,g,v,m,y,w,f,b,$,x,k,z,R,L,q,W,A,M,E,Z,C,O=t=>t;const F={pipeline:"Pipeline",language:"Language"},P={engine:"Engine"},T={engine:"Engine"},S={engine:"Engine",language:"Language",intent_input:"Input"},j={engine:"Engine",language:"Language",voice:"Voice",tts_input:"Input"},V={ready:0,wake_word:1,stt:2,intent:3,tts:4,done:5,error:6},H=(t,e)=>t.init_options?V[t.init_options.start_stage]<=V[e]&&V[e]<=V[t.init_options.end_stage]:e in t,B=(t,e,i)=>"error"in t&&i===e?(0,s.qy)(c||(c=O`
    <ha-alert alert-type="error">
      ${0} (${0})
    </ha-alert>
  `),t.error.message,t.error.code):"",D=(t,e,i,a="-start")=>{const n=e.events.find((t=>t.type===`${i}`+a)),o=e.events.find((t=>t.type===`${i}-end`));if(!n)return"";if(!o)return"error"in e?(0,s.qy)(u||(u=O`❌`)):(0,s.qy)(_||(_=O` <ha-spinner size="small"></ha-spinner> `));const r=new Date(o.timestamp).getTime()-new Date(n.timestamp).getTime(),d=(0,l.ZV)(r/1e3,t.locale,{maximumFractionDigits:2});return(0,s.qy)(g||(g=O`${0}s ✅`),d)},U=(t,e)=>Object.entries(e).map((([e,i])=>(0,s.qy)(v||(v=O`
      <div class="row">
        <div>${0}</div>
        <div>${0}</div>
      </div>
    `),i,t[e]))),I=(t,e)=>{const i={};let a=!1;for(const s in t)s in e||"done"===s||(a=!0,i[s]=t[s]);return a?(0,s.qy)(m||(m=O`<ha-expansion-panel>
        <span slot="header">Raw</span>
        <ha-yaml-editor readOnly autoUpdate .value=${0}></ha-yaml-editor>
      </ha-expansion-panel>`),i):""};class N extends s.WF{render(){var t,e,i,a;const n=this.pipelineRun&&["tts","intent","stt","wake_word"].find((t=>t in this.pipelineRun))||"ready",o=[],r=(this.pipelineRun.init_options&&"text"in this.pipelineRun.init_options.input?this.pipelineRun.init_options.input.text:void 0)||(null===(t=this.pipelineRun)||void 0===t||null===(t=t.stt)||void 0===t||null===(t=t.stt_output)||void 0===t?void 0:t.text)||(null===(e=this.pipelineRun)||void 0===e||null===(e=e.intent)||void 0===e?void 0:e.intent_input);return r&&o.push({from:"user",text:r}),null!==(i=this.pipelineRun)&&void 0!==i&&null!==(i=i.intent)&&void 0!==i&&null!==(i=i.intent_output)&&void 0!==i&&null!==(i=i.response)&&void 0!==i&&null!==(i=i.speech)&&void 0!==i&&null!==(i=i.plain)&&void 0!==i&&i.speech&&o.push({from:"hass",text:this.pipelineRun.intent.intent_output.response.speech.plain.speech}),(0,s.qy)(y||(y=O`
      <ha-card>
        <div class="card-content">
          <div class="row heading">
            <div>Run</div>
            <div>${0}</div>
          </div>

          ${0}
          ${0}
        </div>
      </ha-card>

      ${0}
      ${0}
      ${0}
      ${0}
      ${0}
      ${0}
      ${0}
      ${0}
      ${0}
      <ha-card>
        <ha-expansion-panel>
          <span slot="header">Raw</span>
          <ha-yaml-editor
            read-only
            auto-update
            .value=${0}
          ></ha-yaml-editor>
        </ha-expansion-panel>
      </ha-card>
    `),this.pipelineRun.stage,U(this.pipelineRun.run,F),o.length>0?(0,s.qy)(w||(w=O`
                <div class="messages">
                  ${0}
                </div>
                <div style="clear:both"></div>
              `),o.map((({from:t,text:e})=>(0,s.qy)(f||(f=O`
                      <div class=${0}>${0}</div>
                    `),`message ${t}`,e)))):"",B(this.pipelineRun,"ready",n),H(this.pipelineRun,"wake_word")?(0,s.qy)(b||(b=O`
            <ha-card>
              <div class="card-content">
                <div class="row heading">
                  <span>Wake word</span>
                  ${0}
                </div>
                ${0}
              </div>
            </ha-card>
          `),D(this.hass,this.pipelineRun,"wake_word"),this.pipelineRun.wake_word?(0,s.qy)($||($=O`
                      <div class="card-content">
                        ${0}
                        ${0}
                        ${0}
                      </div>
                    `),U(this.pipelineRun.wake_word,T),this.pipelineRun.wake_word.wake_word_output?(0,s.qy)(x||(x=O`<div class="row">
                                <div>Model</div>
                                <div>
                                  ${0}
                                </div>
                              </div>
                              <div class="row">
                                <div>Timestamp</div>
                                <div>
                                  ${0}
                                </div>
                              </div>`),this.pipelineRun.wake_word.wake_word_output.ww_id,this.pipelineRun.wake_word.wake_word_output.timestamp):"",I(this.pipelineRun.wake_word,P)):""):"",B(this.pipelineRun,"wake_word",n),H(this.pipelineRun,"stt")?(0,s.qy)(k||(k=O`
            <ha-card>
              <div class="card-content">
                <div class="row heading">
                  <span>Speech-to-text</span>
                  ${0}
                </div>
                ${0}
              </div>
            </ha-card>
          `),D(this.hass,this.pipelineRun,"stt","-vad-end"),this.pipelineRun.stt?(0,s.qy)(z||(z=O`
                      <div class="card-content">
                        ${0}
                        <div class="row">
                          <div>Language</div>
                          <div>${0}</div>
                        </div>
                        ${0}
                        ${0}
                      </div>
                    `),U(this.pipelineRun.stt,T),this.pipelineRun.stt.metadata.language,this.pipelineRun.stt.stt_output?(0,s.qy)(R||(R=O`<div class="row">
                              <div>Output</div>
                              <div>${0}</div>
                            </div>`),this.pipelineRun.stt.stt_output.text):"",I(this.pipelineRun.stt,T)):""):"",B(this.pipelineRun,"stt",n),H(this.pipelineRun,"intent")?(0,s.qy)(L||(L=O`
            <ha-card>
              <div class="card-content">
                <div class="row heading">
                  <span>Natural Language Processing</span>
                  ${0}
                </div>
                ${0}
              </div>
            </ha-card>
          `),D(this.hass,this.pipelineRun,"intent"),this.pipelineRun.intent?(0,s.qy)(q||(q=O`
                      <div class="card-content">
                        ${0}
                        ${0}
                        <div class="row">
                          <div>Prefer handling locally</div>
                          <div>
                            ${0}
                          </div>
                        </div>
                        <div class="row">
                          <div>Processed locally</div>
                          <div>
                            ${0}
                          </div>
                        </div>
                        ${0}
                      </div>
                    `),U(this.pipelineRun.intent,S),this.pipelineRun.intent.intent_output?(0,s.qy)(W||(W=O`<div class="row">
                                <div>Response type</div>
                                <div>
                                  ${0}
                                </div>
                              </div>
                              ${0}`),this.pipelineRun.intent.intent_output.response.response_type,"error"===this.pipelineRun.intent.intent_output.response.response_type?(0,s.qy)(A||(A=O`<div class="row">
                                    <div>Error code</div>
                                    <div>
                                      ${0}
                                    </div>
                                  </div>`),this.pipelineRun.intent.intent_output.response.data.code):""):"",this.pipelineRun.intent.prefer_local_intents,this.pipelineRun.intent.processed_locally,I(this.pipelineRun.intent,S)):""):"",B(this.pipelineRun,"intent",n),H(this.pipelineRun,"tts")?(0,s.qy)(M||(M=O`
            <ha-card>
              <div class="card-content">
                <div class="row heading">
                  <span>Text-to-speech</span>
                  ${0}
                </div>
                ${0}
              </div>
              ${0}
            </ha-card>
          `),D(this.hass,this.pipelineRun,"tts"),this.pipelineRun.tts?(0,s.qy)(E||(E=O`
                      <div class="card-content">
                        ${0}
                        ${0}
                      </div>
                    `),U(this.pipelineRun.tts,j),I(this.pipelineRun.tts,j)):"",null!==(a=this.pipelineRun)&&void 0!==a&&null!==(a=a.tts)&&void 0!==a&&a.tts_output?(0,s.qy)(Z||(Z=O`
                    <div class="card-actions">
                      <ha-button @click=${0}>
                        Play Audio
                      </ha-button>
                    </div>
                  `),this._playTTS):""):"",B(this.pipelineRun,"tts",n),this.pipelineRun)}_playTTS(){const t=this.pipelineRun.tts.tts_output.url,e=new Audio(t);e.addEventListener("error",(()=>{(0,p.K$)(this,{title:"Error",text:"Error playing audio"})})),e.addEventListener("canplaythrough",(()=>{e.play()}))}}N.styles=(0,s.AH)(C||(C=O`
    :host {
      display: block;
    }
    ha-card,
    ha-alert {
      display: block;
      margin-bottom: 16px;
    }
    .row {
      display: flex;
      justify-content: space-between;
    }
    .row > div:last-child {
      text-align: right;
    }
    ha-expansion-panel {
      padding-left: 8px;
      padding-inline-start: 8px;
      padding-inline-end: initial;
    }
    .card-content ha-expansion-panel {
      padding-left: 0px;
      padding-inline-start: 0px;
      padding-inline-end: initial;
      --expansion-panel-summary-padding: 0px;
      --expansion-panel-content-padding: 0px;
    }
    .heading {
      font-weight: var(--ha-font-weight-medium);
      margin-bottom: 16px;
    }

    .messages {
      margin-top: 8px;
    }

    .message {
      font-size: var(--ha-font-size-l);
      margin: 8px 0;
      padding: 8px;
      border-radius: 15px;
      clear: both;
    }

    .message.user {
      margin-left: 24px;
      margin-inline-start: 24px;
      margin-inline-end: initial;
      float: var(--float-end);
      text-align: right;
      border-bottom-right-radius: 0px;
      background-color: var(--light-primary-color);
      color: var(--text-light-primary-color, var(--primary-text-color));
      direction: var(--direction);
    }

    .message.hass {
      margin-right: 24px;
      margin-inline-end: 24px;
      margin-inline-start: initial;
      float: var(--float-start);
      border-bottom-left-radius: 0px;
      background-color: var(--primary-color);
      color: var(--text-primary-color);
      direction: var(--direction);
    }
  `)),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],N.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],N.prototype,"pipelineRun",void 0),N=(0,a.__decorate)([(0,n.EM)("assist-render-pipeline-run")],N),e()}catch(c){e(c)}}))},16403:function(t,e,i){i.a(t,(async function(t,a){try{i.r(e),i.d(e,{DialogVoiceAssistantPipelineDetail:function(){return R}});i(35748),i(65315),i(22416),i(59023),i(12977),i(5934),i(56660),i(95013);var s=i(69868),n=i(84922),o=i(11991),r=i(65940),l=i(73120),d=i(20674),p=i(92830),h=i(76943),c=(i(96997),i(75518),i(25223),i(85023)),u=i(83566),_=(i(47474),i(75787),i(1783),i(53751)),g=(i(54641),i(55485)),v=t([h,_,g]);[h,_,g]=v.then?(await v)():v;let m,y,w,f,b,$,x=t=>t;const k="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",z="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z";class R extends n.WF{showDialog(t){if(this._params=t,this._error=void 0,this._cloudActive=this._params.cloudActiveSubscription,this._params.pipeline)return this._data=Object.assign({prefer_local_intents:!1},this._params.pipeline),void(this._hideWakeWord=this._params.hideWakeWord||!this._data.wake_word_entity);let e,i;if(this._hideWakeWord=!0,this._cloudActive)for(const a of Object.values(this.hass.entities))if("cloud"===a.platform)if("stt"===(0,p.m)(a.entity_id)){if(e=a.entity_id,i)break}else if("tts"===(0,p.m)(a.entity_id)&&(i=a.entity_id,e))break;this._data={language:(this.hass.config.language||this.hass.locale.language).substring(0,2),stt_engine:e,tts_engine:i}}closeDialog(){this._params=void 0,this._data=void 0,this._hideWakeWord=!1,(0,l.r)(this,"dialog-closed",{dialog:this.localName})}firstUpdated(){this._getSupportedLanguages()}async _getSupportedLanguages(){const{languages:t}=await(0,c.ds)(this.hass);this._supportedLanguages=t}render(){var t,e,i;if(!this._params||!this._data)return n.s6;const a=null!==(t=this._params.pipeline)&&void 0!==t&&t.id?this._params.pipeline.name:this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.add_assistant_title");return(0,n.qy)(m||(m=x`
      <ha-dialog
        open
        @closed=${0}
        scrimClickAction
        escapeKeyAction
        .heading=${0}
      >
        <ha-dialog-header slot="heading">
          <ha-icon-button
            slot="navigationIcon"
            dialogAction="cancel"
            .label=${0}
            .path=${0}
          ></ha-icon-button>
          <span slot="title" .title=${0}>${0}</span>
          ${0}
        </ha-dialog-header>
        <div class="content">
          ${0}
          <assist-pipeline-detail-config
            .hass=${0}
            .data=${0}
            .supportedLanguages=${0}
            keys="name,language"
            @value-changed=${0}
            ?dialogInitialFocus=${0}
          ></assist-pipeline-detail-config>
          <assist-pipeline-detail-conversation
            .hass=${0}
            .data=${0}
            keys="conversation_engine,conversation_language,prefer_local_intents"
            @value-changed=${0}
          ></assist-pipeline-detail-conversation>
          ${0}
          <assist-pipeline-detail-stt
            .hass=${0}
            .data=${0}
            keys="stt_engine,stt_language"
            @value-changed=${0}
          ></assist-pipeline-detail-stt>
          <assist-pipeline-detail-tts
            .hass=${0}
            .data=${0}
            keys="tts_engine,tts_language,tts_voice"
            @value-changed=${0}
          ></assist-pipeline-detail-tts>
          ${0}
        </div>
        <ha-button
          slot="primaryAction"
          @click=${0}
          .disabled=${0}
          dialogInitialFocus
        >
          ${0}
        </ha-button>
      </ha-dialog>
    `),this.closeDialog,a,this.hass.localize("ui.common.close"),k,a,a,this._hideWakeWord&&!this._params.hideWakeWord&&this._hasWakeWorkEntities(this.hass.states)?(0,n.qy)(y||(y=x`<ha-button-menu
                slot="actionItems"
                @action=${0}
                @closed=${0}
                menu-corner="END"
                corner="BOTTOM_END"
              >
                <ha-icon-button
                  .path=${0}
                  slot="trigger"
                ></ha-icon-button>
                <ha-list-item>
                  ${0}
                </ha-list-item></ha-button-menu
              >`),this._handleShowWakeWord,d.d,z,this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.add_streaming_wake_word")):n.s6,this._error?(0,n.qy)(w||(w=x`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):n.s6,this.hass,this._data,this._supportedLanguages,this._valueChanged,!(null!==(e=this._params.pipeline)&&void 0!==e&&e.id),this.hass,this._data,this._valueChanged,this._cloudActive||"cloud"!==this._data.tts_engine&&"cloud"!==this._data.stt_engine?n.s6:(0,n.qy)(f||(f=x`
                <ha-alert alert-type="warning">
                  ${0}
                  <ha-button size="small" href="/config/cloud" slot="action">
                    ${0}
                  </ha-button>
                </ha-alert>
              `),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.no_cloud_message"),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.no_cloud_action")),this.hass,this._data,this._valueChanged,this.hass,this._data,this._valueChanged,this._hideWakeWord?n.s6:(0,n.qy)(b||(b=x`<assist-pipeline-detail-wakeword
                .hass=${0}
                .data=${0}
                keys="wake_word_entity,wake_word_id"
                @value-changed=${0}
              ></assist-pipeline-detail-wakeword>`),this.hass,this._data,this._valueChanged),this._updatePipeline,this._submitting,null!==(i=this._params.pipeline)&&void 0!==i&&i.id?this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.update_assistant_action"):this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.add_assistant_action"))}_handleShowWakeWord(){this._hideWakeWord=!1}_valueChanged(t){this._error=void 0;const e={};t.currentTarget.getAttribute("keys").split(",").forEach((i=>{e[i]=t.detail.value[i]})),this._data=Object.assign(Object.assign({},this._data),e)}async _updatePipeline(){this._submitting=!0;try{var t,e,i,a,s,n,o,r,l,d;const p=this._data,h={name:p.name,language:p.language,conversation_engine:p.conversation_engine,conversation_language:null!==(t=p.conversation_language)&&void 0!==t?t:null,prefer_local_intents:null===(e=p.prefer_local_intents)||void 0===e||e,stt_engine:null!==(i=p.stt_engine)&&void 0!==i?i:null,stt_language:null!==(a=p.stt_language)&&void 0!==a?a:null,tts_engine:null!==(s=p.tts_engine)&&void 0!==s?s:null,tts_language:null!==(n=p.tts_language)&&void 0!==n?n:null,tts_voice:null!==(o=p.tts_voice)&&void 0!==o?o:null,wake_word_entity:null!==(r=p.wake_word_entity)&&void 0!==r?r:null,wake_word_id:null!==(l=p.wake_word_id)&&void 0!==l?l:null};null!==(d=this._params.pipeline)&&void 0!==d&&d.id?await this._params.updatePipeline(h):this._params.createPipeline?await this._params.createPipeline(h):console.error("No createPipeline function provided"),this.closeDialog()}catch(p){this._error=(null==p?void 0:p.message)||"Unknown error"}finally{this._submitting=!1}}static get styles(){return[u.nA,(0,n.AH)($||($=x`
        .content > *:not(:last-child) {
          margin-bottom: 16px;
          display: block;
        }
        ha-alert {
          margin-bottom: 16px;
          display: block;
        }
        a {
          text-decoration: none;
        }
      `))]}constructor(...t){super(...t),this._hideWakeWord=!1,this._submitting=!1,this._hasWakeWorkEntities=(0,r.A)((t=>Object.keys(t).some((t=>t.startsWith("wake_word.")))))}}(0,s.__decorate)([(0,o.MZ)({attribute:!1})],R.prototype,"hass",void 0),(0,s.__decorate)([(0,o.wk)()],R.prototype,"_params",void 0),(0,s.__decorate)([(0,o.wk)()],R.prototype,"_data",void 0),(0,s.__decorate)([(0,o.wk)()],R.prototype,"_hideWakeWord",void 0),(0,s.__decorate)([(0,o.wk)()],R.prototype,"_cloudActive",void 0),(0,s.__decorate)([(0,o.wk)()],R.prototype,"_error",void 0),(0,s.__decorate)([(0,o.wk)()],R.prototype,"_submitting",void 0),(0,s.__decorate)([(0,o.wk)()],R.prototype,"_supportedLanguages",void 0),R=(0,s.__decorate)([(0,o.EM)("dialog-voice-assistant-pipeline-detail")],R),a()}catch(m){a(m)}}))}}]);
//# sourceMappingURL=4848.7cf73843638a565a.js.map