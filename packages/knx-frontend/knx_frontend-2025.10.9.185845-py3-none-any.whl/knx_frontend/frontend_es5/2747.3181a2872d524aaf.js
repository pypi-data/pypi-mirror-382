"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2747"],{83490:function(t,e,s){s.d(e,{I:function(){return o}});s(46852),s(99342),s(65315),s(22416),s(36874),s(12977),s(54323);class a{addFromStorage(t){if(!this._storage[t]){const e=this.storage.getItem(t);e&&(this._storage[t]=JSON.parse(e))}}subscribeChanges(t,e){return this._listeners[t]?this._listeners[t].push(e):this._listeners[t]=[e],()=>{this.unsubscribeChanges(t,e)}}unsubscribeChanges(t,e){if(!(t in this._listeners))return;const s=this._listeners[t].indexOf(e);-1!==s&&this._listeners[t].splice(s,1)}hasKey(t){return t in this._storage}getValue(t){return this._storage[t]}setValue(t,e){const s=this._storage[t];this._storage[t]=e;try{void 0===e?this.storage.removeItem(t):this.storage.setItem(t,JSON.stringify(e))}catch(a){}finally{this._listeners[t]&&this._listeners[t].forEach((t=>t(s,e)))}}constructor(t=window.localStorage){this._storage={},this._listeners={},this.storage=t,this.storage===window.localStorage&&window.addEventListener("storage",(t=>{t.key&&this.hasKey(t.key)&&(this._storage[t.key]=t.newValue?JSON.parse(t.newValue):t.newValue,this._listeners[t.key]&&this._listeners[t.key].forEach((e=>e(t.oldValue?JSON.parse(t.oldValue):t.oldValue,this._storage[t.key]))))}))}}const i={};function o(t){return(e,s)=>{if("object"==typeof s)throw new Error("This decorator does not support this compilation type.");const o=t.storage||"localStorage";let r;o&&o in i?r=i[o]:(r=new a(window[o]),i[o]=r);const n=t.key||String(s);r.addFromStorage(n);const l=!1!==t.subscribe?t=>r.subscribeChanges(n,((e,a)=>{t.requestUpdate(s,e)})):void 0,h=()=>r.hasKey(n)?t.deserializer?t.deserializer(r.getValue(n)):r.getValue(n):void 0,c=(e,a)=>{let i;t.state&&(i=h()),r.setValue(n,t.serializer?t.serializer(a):a),t.state&&e.requestUpdate(s,i)},d=e.performUpdate;if(e.performUpdate=function(){this.__initialized=!0,d.call(this)},t.subscribe){const t=e.connectedCallback,s=e.disconnectedCallback;e.connectedCallback=function(){t.call(this);const e=this;e.__unbsubLocalStorage||(e.__unbsubLocalStorage=null==l?void 0:l(this))},e.disconnectedCallback=function(){var t;s.call(this);const e=this;null===(t=e.__unbsubLocalStorage)||void 0===t||t.call(e),e.__unbsubLocalStorage=void 0}}const u=Object.getOwnPropertyDescriptor(e,s);let g;if(void 0===u)g={get(){return h()},set(t){(this.__initialized||void 0===h())&&c(this,t)},configurable:!0,enumerable:!0};else{const t=u.set;g=Object.assign(Object.assign({},u),{},{get(){return h()},set(e){(this.__initialized||void 0===h())&&c(this,e),null==t||t.call(this,e)}})}Object.defineProperty(e,s,g)}}},84747:function(t,e,s){s.a(t,(async function(t,e){try{s(35748),s(95013);var a=s(69868),i=s(84922),o=s(11991),r=s(75907),n=s(76943),l=s(71622),h=(s(95635),t([n,l]));[n,l]=h.then?(await h)():h;let c,d,u,g,p,_,v=t=>t;const y="M2.2,16.06L3.88,12L2.2,7.94L6.26,6.26L7.94,2.2L12,3.88L16.06,2.2L17.74,6.26L21.8,7.94L20.12,12L21.8,16.06L17.74,17.74L16.06,21.8L12,20.12L7.94,21.8L6.26,17.74L2.2,16.06M13,17V15H11V17H13M13,13V7H11V13H13Z",b="M9,20.42L2.79,14.21L5.62,11.38L9,14.77L18.88,4.88L21.71,7.71L9,20.42Z";class m extends i.WF{render(){const t=this.progress||this._result?"accent":this.appearance;return(0,i.qy)(c||(c=v`
      <ha-button
        .appearance=${0}
        .disabled=${0}
        .loading=${0}
        .variant=${0}
        class=${0}
      >
        ${0}

        <slot>${0}</slot>
      </ha-button>
      ${0}
    `),t,this.disabled,this.progress,"success"===this._result?"success":"error"===this._result?"danger":this.variant,(0,r.H)({result:!!this._result,success:"success"===this._result,error:"error"===this._result}),this.iconPath?(0,i.qy)(d||(d=v`<ha-svg-icon
              .path=${0}
              slot="start"
            ></ha-svg-icon>`),this.iconPath):i.s6,this.label,this._result?(0,i.qy)(u||(u=v`
            <div class="progress">
              ${0}
            </div>
          `),"success"===this._result?(0,i.qy)(g||(g=v`<ha-svg-icon .path=${0}></ha-svg-icon>`),b):"error"===this._result?(0,i.qy)(p||(p=v`<ha-svg-icon .path=${0}></ha-svg-icon>`),y):i.s6):i.s6)}actionSuccess(){this._setResult("success")}actionError(){this._setResult("error")}_setResult(t){this._result=t,setTimeout((()=>{this._result=void 0}),2e3)}constructor(...t){super(...t),this.disabled=!1,this.progress=!1,this.appearance="accent",this.variant="brand"}}m.styles=(0,i.AH)(_||(_=v`
    :host {
      outline: none;
      display: inline-block;
      position: relative;
    }

    :host([progress]) {
      pointer-events: none;
    }

    .progress {
      bottom: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      position: absolute;
      top: 0;
      width: 100%;
    }

    ha-button {
      width: 100%;
    }

    ha-button.result::part(start),
    ha-button.result::part(end),
    ha-button.result::part(label),
    ha-button.result::part(caret),
    ha-button.result::part(spinner) {
      visibility: hidden;
    }

    ha-svg-icon {
      color: var(--white-color);
    }
  `)),(0,a.__decorate)([(0,o.MZ)()],m.prototype,"label",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],m.prototype,"disabled",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean,reflect:!0})],m.prototype,"progress",void 0),(0,a.__decorate)([(0,o.MZ)()],m.prototype,"appearance",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],m.prototype,"iconPath",void 0),(0,a.__decorate)([(0,o.MZ)()],m.prototype,"variant",void 0),(0,a.__decorate)([(0,o.wk)()],m.prototype,"_result",void 0),m=(0,a.__decorate)([(0,o.EM)("ha-progress-button")],m),e()}catch(c){e(c)}}))},55910:function(t,e,s){s.a(t,(async function(t,a){try{s.r(e),s.d(e,{TTSTryDialog:function(){return m}});s(35748),s(12977),s(5934),s(95013);var i=s(69868),o=s(84922),r=s(11991),n=s(83490),l=s(73120),h=s(84747),c=s(72847),d=(s(79973),s(87608)),u=s(83566),g=s(47420),p=t([h]);h=(p.then?(await p)():p)[0];let _,v,y=t=>t;const b="M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M10,16.5L16,12L10,7.5V16.5Z";class m extends o.WF{showDialog(t){this._params=t,this._valid=Boolean(this._defaultMessage)}closeDialog(){this._params=void 0,(0,l.r)(this,"dialog-closed",{dialog:this.localName})}get _defaultMessage(){var t,e;const s=null===(t=this._params.language)||void 0===t?void 0:t.substring(0,2),a=this.hass.locale.language.substring(0,2);return s&&null!==(e=this._messages)&&void 0!==e&&e[s]?this._messages[s]:s===a?this.hass.localize("ui.dialogs.tts-try.message_example"):""}render(){return this._params?(0,o.qy)(_||(_=y`
      <ha-dialog
        open
        @closed=${0}
        .heading=${0}
      >
        <ha-textarea
          autogrow
          id="message"
          .label=${0}
          .placeholder=${0}
          .value=${0}
          @input=${0}
          ?dialogInitialFocus=${0}
        >
        </ha-textarea>

        <ha-progress-button
          .progress=${0}
          ?dialogInitialFocus=${0}
          slot="primaryAction"
          @click=${0}
          .disabled=${0}
          .iconPath=${0}
        >
          ${0}
        </ha-progress-button>
      </ha-dialog>
    `),this.closeDialog,(0,c.l)(this.hass,this.hass.localize("ui.dialogs.tts-try.header")),this.hass.localize("ui.dialogs.tts-try.message"),this.hass.localize("ui.dialogs.tts-try.message_placeholder"),this._defaultMessage,this._inputChanged,!this._defaultMessage,this._loadingExample,Boolean(this._defaultMessage),this._playExample,!this._valid,b,this.hass.localize("ui.dialogs.tts-try.play")):o.s6}async _inputChanged(){var t;this._valid=Boolean(null===(t=this._messageInput)||void 0===t?void 0:t.value)}async _playExample(){var t;const e=null===(t=this._messageInput)||void 0===t?void 0:t.value;if(!e)return;const s=this._params.engine,a=this._params.language,i=this._params.voice;a&&(this._messages=Object.assign(Object.assign({},this._messages),{},{[a.substring(0,2)]:e})),this._loadingExample=!0;const o=new Audio;let r;o.play();try{r=(await(0,d.S_)(this.hass,{platform:s,message:e,language:a,options:{voice:i}})).path}catch(n){return this._loadingExample=!1,void(0,g.K$)(this,{text:`Unable to load example. ${n.error||n.body||n}`,warning:!0})}o.src=r,o.addEventListener("canplaythrough",(()=>o.play())),o.addEventListener("playing",(()=>{this._loadingExample=!1})),o.addEventListener("error",(()=>{(0,g.K$)(this,{title:"Error playing audio."}),this._loadingExample=!1}))}constructor(...t){super(...t),this._loadingExample=!1,this._valid=!1}}m.styles=[u.nA,(0,o.AH)(v||(v=y`
      ha-dialog {
        --mdc-dialog-max-width: 500px;
      }
      ha-textarea,
      ha-select {
        width: 100%;
      }
      ha-select {
        margin-top: 8px;
      }
      .loading {
        height: 36px;
      }
    `))],(0,i.__decorate)([(0,r.MZ)({attribute:!1})],m.prototype,"hass",void 0),(0,i.__decorate)([(0,r.wk)()],m.prototype,"_loadingExample",void 0),(0,i.__decorate)([(0,r.wk)()],m.prototype,"_params",void 0),(0,i.__decorate)([(0,r.wk)()],m.prototype,"_valid",void 0),(0,i.__decorate)([(0,r.P)("#message")],m.prototype,"_messageInput",void 0),(0,i.__decorate)([(0,n.I)({key:"ttsTryMessages",state:!1,subscribe:!1})],m.prototype,"_messages",void 0),m=(0,i.__decorate)([(0,r.EM)("dialog-tts-try")],m),a()}catch(_){a(_)}}))}}]);
//# sourceMappingURL=2747.3181a2872d524aaf.js.map