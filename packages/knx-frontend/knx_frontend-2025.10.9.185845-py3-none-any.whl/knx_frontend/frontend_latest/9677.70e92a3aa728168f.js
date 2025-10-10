export const __webpack_id__="9677";export const __webpack_ids__=["9677"];export const __webpack_modules__={89969:function(e,t,r){r.r(t),r.d(t,{HaLabelSelector:()=>n});var a=r(69868),o=r(84922),s=r(11991),i=r(26846),l=r(73120);r(95403);class n extends o.WF{render(){return this.selector.label.multiple?o.qy`
        <ha-labels-picker
          no-add
          .hass=${this.hass}
          .value=${(0,i.e)(this.value??[])}
          .required=${this.required}
          .disabled=${this.disabled}
          .label=${this.label}
          @value-changed=${this._handleChange}
        >
        </ha-labels-picker>
      `:o.qy`
      <ha-label-picker
        no-add
        .hass=${this.hass}
        .value=${this.value}
        .required=${this.required}
        .disabled=${this.disabled}
        .label=${this.label}
        @value-changed=${this._handleChange}
      >
      </ha-label-picker>
    `}_handleChange(e){let t=e.detail.value;this.value!==t&&((""===t||Array.isArray(t)&&0===t.length)&&!this.required&&(t=void 0),(0,l.r)(this,"value-changed",{value:t}))}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}n.styles=o.AH`
    ha-labels-picker {
      display: block;
      width: 100%;
    }
  `,(0,a.__decorate)([(0,s.MZ)({attribute:!1})],n.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)()],n.prototype,"value",void 0),(0,a.__decorate)([(0,s.MZ)()],n.prototype,"name",void 0),(0,a.__decorate)([(0,s.MZ)()],n.prototype,"label",void 0),(0,a.__decorate)([(0,s.MZ)()],n.prototype,"placeholder",void 0),(0,a.__decorate)([(0,s.MZ)()],n.prototype,"helper",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],n.prototype,"selector",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],n.prototype,"disabled",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],n.prototype,"required",void 0),n=(0,a.__decorate)([(0,s.EM)("ha-selector-label")],n)},47308:function(e,t,r){r.d(t,{N:()=>s});const a=e=>{let t=[];function r(r,a){e=a?r:Object.assign(Object.assign({},e),r);let o=t;for(let t=0;t<o.length;t++)o[t](e)}return{get state(){return e},action(t){function a(e){r(e,!1)}return function(){let r=[e];for(let e=0;e<arguments.length;e++)r.push(arguments[e]);let o=t.apply(this,r);if(null!=o)return o instanceof Promise?o.then(a):a(o)}},setState:r,clearState(){e=void 0},subscribe(e){return t.push(e),()=>{!function(e){let r=[];for(let a=0;a<t.length;a++)t[a]===e?e=null:r.push(t[a]);t=r}(e)}}}},o=(e,t,r,o,s={unsubGrace:!0})=>{if(e[t])return e[t];let i,l,n=0,d=a();const c=()=>{if(!r)throw new Error("Collection does not support refresh");return r(e).then((e=>d.setState(e,!0)))},u=()=>c().catch((t=>{if(e.connected)throw t})),h=()=>{l=void 0,i&&i.then((e=>{e()})),d.clearState(),e.removeEventListener("ready",c),e.removeEventListener("disconnected",p)},p=()=>{l&&(clearTimeout(l),h())};return e[t]={get state(){return d.state},refresh:c,subscribe(t){n++,1===n&&(()=>{if(void 0!==l)return clearTimeout(l),void(l=void 0);o&&(i=o(e,d)),r&&(e.addEventListener("ready",u),u()),e.addEventListener("disconnected",p)})();const a=d.subscribe(t);return void 0!==d.state&&setTimeout((()=>t(d.state)),0),()=>{a(),n--,n||(s.unsubGrace?l=setTimeout(h,5e3):h())}}},e[t]},s=(e,t,r,a,s)=>o(a,e,t,r).subscribe(s)}};
//# sourceMappingURL=9677.70e92a3aa728168f.js.map