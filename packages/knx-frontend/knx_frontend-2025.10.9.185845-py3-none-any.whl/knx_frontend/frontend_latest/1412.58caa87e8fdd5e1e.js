export const __webpack_id__="1412";export const __webpack_ids__=["1412"];export const __webpack_modules__={13125:function(e,t,i){i.a(e,(async function(e,s){try{i.d(t,{T:()=>p});var a=i(96904),r=i(65940),n=e([a]);a=(n.then?(await n)():n)[0];const p=(e,t)=>{try{return d(t)?.of(e)??e}catch{return e}},d=(0,r.A)((e=>new Intl.DisplayNames(e.language,{type:"language",fallback:"code"})));s()}catch(p){s(p)}}))},46102:function(e,t,i){i.a(e,(async function(e,t){try{var s=i(69868),a=i(84922),r=i(11991),n=i(73120),p=i(20674),d=i(13125),l=i(85023),o=(i(25223),i(37207),e([d]));d=(o.then?(await o)():o)[0];const c="preferred",_="last_used";class u extends a.WF{get _default(){return this.includeLastUsed?_:c}render(){if(!this._pipelines)return a.s6;const e=this.value??this._default;return a.qy`
      <ha-select
        .label=${this.label||this.hass.localize("ui.components.pipeline-picker.pipeline")}
        .value=${e}
        .required=${this.required}
        .disabled=${this.disabled}
        @selected=${this._changed}
        @closed=${p.d}
        fixedMenuPosition
        naturalMenuWidth
      >
        ${this.includeLastUsed?a.qy`
              <ha-list-item .value=${_}>
                ${this.hass.localize("ui.components.pipeline-picker.last_used")}
              </ha-list-item>
            `:null}
        <ha-list-item .value=${c}>
          ${this.hass.localize("ui.components.pipeline-picker.preferred",{preferred:this._pipelines.find((e=>e.id===this._preferredPipeline))?.name})}
        </ha-list-item>
        ${this._pipelines.map((e=>a.qy`<ha-list-item .value=${e.id}>
              ${e.name}
              (${(0,d.T)(e.language,this.hass.locale)})
            </ha-list-item>`))}
      </ha-select>
    `}firstUpdated(e){super.firstUpdated(e),(0,l.nx)(this.hass).then((e=>{this._pipelines=e.pipelines,this._preferredPipeline=e.preferred_pipeline}))}_changed(e){const t=e.target;!this.hass||""===t.value||t.value===this.value||void 0===this.value&&t.value===this._default||(this.value=t.value===this._default?void 0:t.value,(0,n.r)(this,"value-changed",{value:this.value}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.includeLastUsed=!1,this._preferredPipeline=null}}u.styles=a.AH`
    ha-select {
      width: 100%;
    }
  `,(0,s.__decorate)([(0,r.MZ)()],u.prototype,"value",void 0),(0,s.__decorate)([(0,r.MZ)()],u.prototype,"label",void 0),(0,s.__decorate)([(0,r.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],u.prototype,"disabled",void 0),(0,s.__decorate)([(0,r.MZ)({type:Boolean})],u.prototype,"required",void 0),(0,s.__decorate)([(0,r.MZ)({attribute:!1})],u.prototype,"includeLastUsed",void 0),(0,s.__decorate)([(0,r.wk)()],u.prototype,"_pipelines",void 0),(0,s.__decorate)([(0,r.wk)()],u.prototype,"_preferredPipeline",void 0),u=(0,s.__decorate)([(0,r.EM)("ha-assist-pipeline-picker")],u),t()}catch(c){t(c)}}))},22543:function(e,t,i){i.a(e,(async function(e,s){try{i.r(t),i.d(t,{HaAssistPipelineSelector:()=>l});var a=i(69868),r=i(84922),n=i(11991),p=i(46102),d=e([p]);p=(d.then?(await d)():d)[0];class l extends r.WF{render(){return r.qy`
      <ha-assist-pipeline-picker
        .hass=${this.hass}
        .value=${this.value}
        .label=${this.label}
        .helper=${this.helper}
        .disabled=${this.disabled}
        .required=${this.required}
        .includeLastUsed=${Boolean(this.selector.assist_pipeline?.include_last_used)}
      ></ha-assist-pipeline-picker>
    `}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}l.styles=r.AH`
    ha-conversation-agent-picker {
      width: 100%;
    }
  `,(0,a.__decorate)([(0,n.MZ)({attribute:!1})],l.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],l.prototype,"selector",void 0),(0,a.__decorate)([(0,n.MZ)()],l.prototype,"value",void 0),(0,a.__decorate)([(0,n.MZ)()],l.prototype,"label",void 0),(0,a.__decorate)([(0,n.MZ)()],l.prototype,"helper",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],l.prototype,"disabled",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],l.prototype,"required",void 0),l=(0,a.__decorate)([(0,n.EM)("ha-selector-assist_pipeline")],l),s()}catch(l){s(l)}}))},85023:function(e,t,i){i.d(t,{QC:()=>s,ds:()=>l,mp:()=>n,nx:()=>r,u6:()=>p,vU:()=>a,zn:()=>d});const s=(e,t,i)=>"run-start"===t.type?e={init_options:i,stage:"ready",run:t.data,events:[t]}:e?((e="wake_word-start"===t.type?{...e,stage:"wake_word",wake_word:{...t.data,done:!1}}:"wake_word-end"===t.type?{...e,wake_word:{...e.wake_word,...t.data,done:!0}}:"stt-start"===t.type?{...e,stage:"stt",stt:{...t.data,done:!1}}:"stt-end"===t.type?{...e,stt:{...e.stt,...t.data,done:!0}}:"intent-start"===t.type?{...e,stage:"intent",intent:{...t.data,done:!1}}:"intent-end"===t.type?{...e,intent:{...e.intent,...t.data,done:!0}}:"tts-start"===t.type?{...e,stage:"tts",tts:{...t.data,done:!1}}:"tts-end"===t.type?{...e,tts:{...e.tts,...t.data,done:!0}}:"run-end"===t.type?{...e,stage:"done"}:"error"===t.type?{...e,stage:"error",error:t.data}:{...e}).events=[...e.events,t],e):void console.warn("Received unexpected event before receiving session",t),a=(e,t,i)=>e.connection.subscribeMessage(t,{...i,type:"assist_pipeline/run"}),r=e=>e.callWS({type:"assist_pipeline/pipeline/list"}),n=(e,t)=>e.callWS({type:"assist_pipeline/pipeline/get",pipeline_id:t}),p=(e,t)=>e.callWS({type:"assist_pipeline/pipeline/create",...t}),d=(e,t,i)=>e.callWS({type:"assist_pipeline/pipeline/update",pipeline_id:t,...i}),l=e=>e.callWS({type:"assist_pipeline/language/list"})}};
//# sourceMappingURL=1412.58caa87e8fdd5e1e.js.map