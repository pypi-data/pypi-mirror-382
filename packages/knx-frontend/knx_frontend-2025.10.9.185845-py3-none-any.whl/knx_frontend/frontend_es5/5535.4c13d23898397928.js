/*! For license information please see 5535.4c13d23898397928.js.LICENSE.txt */
"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["5535"],{85710:function(t,e,i){i.a(t,(async function(t,e){try{i(35748),i(35058),i(65315),i(37089),i(12977),i(5934),i(95013);var s=i(69868),o=i(84922),a=i(11991),n=i(73120),d=i(88340),r=i(18944),l=(i(99741),i(15648)),h=(i(95635),i(11934),t([l]));l=(h.then?(await h)():h)[0];let c,u=t=>t;const v="M20 2H4C2.9 2 2 2.9 2 4V20C2 21.11 2.9 22 4 22H20C21.11 22 22 21.11 22 20V4C22 2.9 21.11 2 20 2M4 6L6 4H10.9L4 10.9V6M4 13.7L13.7 4H18.6L4 18.6V13.7M20 18L18 20H13.1L20 13.1V18M20 10.3L10.3 20H5.4L20 5.4V10.3Z";class p extends o.WF{render(){var t,e,i,s;const a=(0,r.dj)(this.hass.areas),n=Object.values(this.hass.areas).sort(((t,e)=>a(t.area_id,e.area_id))).map((t=>{var e;const{floor:i}=(0,d.L)(t,this.hass);return{value:t.area_id,label:t.name,icon:null!==(e=t.icon)&&void 0!==e?e:void 0,iconPath:v,description:null==i?void 0:i.name}})),l={order:null!==(t=null===(e=this.value)||void 0===e?void 0:e.order)&&void 0!==t?t:[],hidden:null!==(i=null===(s=this.value)||void 0===s?void 0:s.hidden)&&void 0!==i?i:[]};return(0,o.qy)(c||(c=u`
      <ha-expansion-panel
        outlined
        .header=${0}
        .expanded=${0}
      >
        <ha-svg-icon slot="leading-icon" .path=${0}></ha-svg-icon>
        <ha-items-display-editor
          .hass=${0}
          .items=${0}
          .value=${0}
          @value-changed=${0}
          .showNavigationButton=${0}
        ></ha-items-display-editor>
      </ha-expansion-panel>
    `),this.label,this.expanded,v,this.hass,n,l,this._areaDisplayChanged,this.showNavigationButton)}async _areaDisplayChanged(t){var e,i;t.stopPropagation();const s=t.detail.value,o=Object.assign(Object.assign({},this.value),s);0===(null===(e=o.hidden)||void 0===e?void 0:e.length)&&delete o.hidden,0===(null===(i=o.order)||void 0===i?void 0:i.length)&&delete o.order,(0,n.r)(this,"value-changed",{value:o})}constructor(...t){super(...t),this.expanded=!1,this.disabled=!1,this.required=!1,this.showNavigationButton=!1}}(0,s.__decorate)([(0,a.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,s.__decorate)([(0,a.MZ)()],p.prototype,"label",void 0),(0,s.__decorate)([(0,a.MZ)({attribute:!1})],p.prototype,"value",void 0),(0,s.__decorate)([(0,a.MZ)()],p.prototype,"helper",void 0),(0,s.__decorate)([(0,a.MZ)({type:Boolean})],p.prototype,"expanded",void 0),(0,s.__decorate)([(0,a.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,s.__decorate)([(0,a.MZ)({type:Boolean})],p.prototype,"required",void 0),(0,s.__decorate)([(0,a.MZ)({type:Boolean,attribute:"show-navigation-button"})],p.prototype,"showNavigationButton",void 0),p=(0,s.__decorate)([(0,a.EM)("ha-areas-display-editor")],p),e()}catch(c){e(c)}}))},15648:function(t,e,i){i.a(t,(async function(t,e){try{i(32203),i(79827),i(35748),i(99342),i(35058),i(65315),i(837),i(37089),i(12977),i(5934),i(18223),i(95013);var s=i(69868),o=i(88006),a=i(84922),n=i(11991),d=i(75907),r=i(13802),l=i(33055),h=i(55),c=i(65940),u=i(73120),v=i(20674),p=i(90963),_=(i(81164),i(93672),i(72062),i(5803),i(98343),i(8115),i(95635),t([o]));o=(_.then?(await _)():_)[0];let g,y,m,b,w,x,$,M,C,f,k=t=>t;const I="M7,19V17H9V19H7M11,19V17H13V19H11M15,19V17H17V19H15M7,15V13H9V15H7M11,15V13H13V15H11M15,15V13H17V15H15M7,11V9H9V11H7M11,11V9H13V11H11M15,11V9H17V11H15M7,7V5H9V7H7M11,7V5H13V7H11M15,7V5H17V7H15Z",H="M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z",V="M11.83,9L15,12.16C15,12.11 15,12.05 15,12A3,3 0 0,0 12,9C11.94,9 11.89,9 11.83,9M7.53,9.8L9.08,11.35C9.03,11.56 9,11.77 9,12A3,3 0 0,0 12,15C12.22,15 12.44,14.97 12.65,14.92L14.2,16.47C13.53,16.8 12.79,17 12,17A5,5 0 0,1 7,12C7,11.21 7.2,10.47 7.53,9.8M2,4.27L4.28,6.55L4.73,7C3.08,8.3 1.78,10 1,12C2.73,16.39 7,19.5 12,19.5C13.55,19.5 15.03,19.2 16.38,18.66L16.81,19.08L19.73,22L21,20.73L3.27,3M12,7A5,5 0 0,1 17,12C17,12.64 16.87,13.26 16.64,13.82L19.57,16.75C21.07,15.5 22.27,13.86 23,12C21.27,7.61 17,4.5 12,4.5C10.6,4.5 9.26,4.75 8,5.2L10.17,7.35C10.74,7.13 11.35,7 12,7Z";class Z extends a.WF{render(){const t=this._allItems(this.items,this.value.hidden,this.value.order),e=this._showIcon.value;return(0,a.qy)(g||(g=k`
      <ha-sortable
        draggable-selector=".draggable"
        handle-selector=".handle"
        @item-moved=${0}
      >
        <ha-md-list>
          ${0}
        </ha-md-list>
      </ha-sortable>
    `),this._itemMoved,(0,l.u)(t,(t=>t.value),((t,i)=>{const s=!this.value.hidden.includes(t.value),{label:o,value:n,description:l,icon:c,iconPath:u,disableSorting:p}=t;return(0,a.qy)(y||(y=k`
                <ha-md-list-item
                  type="button"
                  @click=${0}
                  .value=${0}
                  class=${0}
                  @keydown=${0}
                  .idx=${0}
                >
                  <span slot="headline">${0}</span>
                  ${0}
                  ${0}
                  ${0}
                  ${0}
                  <ha-icon-button
                    .path=${0}
                    slot="end"
                    .label=${0}
                    .value=${0}
                    @click=${0}
                  ></ha-icon-button>
                  ${0}
                </ha-md-list-item>
              `),this.showNavigationButton?this._navigate:void 0,n,(0,d.H)({hidden:!s,draggable:s&&!p,"drag-selected":this._dragIndex===i}),s&&!p?this._listElementKeydown:void 0,i,o,l?(0,a.qy)(m||(m=k`<span slot="supporting-text">${0}</span>`),l):a.s6,e?c?(0,a.qy)(b||(b=k`
                          <ha-icon
                            class="icon"
                            .icon=${0}
                            slot="start"
                          ></ha-icon>
                        `),(0,h.T)(c,"")):u?(0,a.qy)(w||(w=k`
                            <ha-svg-icon
                              class="icon"
                              .path=${0}
                              slot="start"
                            ></ha-svg-icon>
                          `),u):a.s6:a.s6,this.showNavigationButton?(0,a.qy)(x||(x=k`
                        <ha-icon-next slot="end"></ha-icon-next>
                        <div slot="end" class="separator"></div>
                      `)):a.s6,this.actionsRenderer?(0,a.qy)($||($=k`
                        <div slot="end" @click=${0}>
                          ${0}
                        </div>
                      `),v.d,this.actionsRenderer(t)):a.s6,s?H:V,this.hass.localize("ui.components.items-display-editor."+(s?"hide":"show"),{label:o}),n,this._toggle,s&&!p?(0,a.qy)(M||(M=k`
                        <ha-svg-icon
                          tabindex=${0}
                          .idx=${0}
                          @keydown=${0}
                          class="handle"
                          .path=${0}
                          slot="end"
                        ></ha-svg-icon>
                      `),(0,r.J)(this.showNavigationButton?"0":void 0),i,this.showNavigationButton?this._dragHandleKeydown:void 0,I):(0,a.qy)(C||(C=k`<ha-svg-icon slot="end"></ha-svg-icon>`)))})))}_toggle(t){t.stopPropagation(),this._dragIndex=null;const e=t.currentTarget.value,i=this._hiddenItems(this.items,this.value.hidden).map((t=>t.value));i.includes(e)?i.splice(i.indexOf(e),1):i.push(e);const s=this._visibleItems(this.items,i,this.value.order).map((t=>t.value));this.value={hidden:i,order:s},(0,u.r)(this,"value-changed",{value:this.value})}_itemMoved(t){t.stopPropagation();const{oldIndex:e,newIndex:i}=t.detail;this._moveItem(e,i)}_moveItem(t,e){if(t===e)return;const i=this._visibleItems(this.items,this.value.hidden,this.value.order).map((t=>t.value)),s=i.splice(t,1)[0];i.splice(e,0,s),this.value=Object.assign(Object.assign({},this.value),{},{order:i}),(0,u.r)(this,"value-changed",{value:this.value})}_navigate(t){const e=t.currentTarget.value;(0,u.r)(this,"item-display-navigate-clicked",{value:e}),t.stopPropagation()}_dragHandleKeydown(t){"Enter"!==t.key&&" "!==t.key||(t.preventDefault(),t.stopPropagation(),null===this._dragIndex?(this._dragIndex=t.target.idx,this.addEventListener("keydown",this._sortKeydown)):(this.removeEventListener("keydown",this._sortKeydown),this._dragIndex=null))}disconnectedCallback(){super.disconnectedCallback(),this.removeEventListener("keydown",this._sortKeydown)}constructor(...t){super(...t),this.items=[],this.showNavigationButton=!1,this.dontSortVisible=!1,this.value={order:[],hidden:[]},this._dragIndex=null,this._showIcon=new o.P(this,{callback:t=>{var e;return(null===(e=t[0])||void 0===e?void 0:e.contentRect.width)>450}}),this._visibleItems=(0,c.A)(((t,e,i)=>{const s=(0,p.u1)(i),o=t.filter((t=>!e.includes(t.value)));return this.dontSortVisible?[...o.filter((t=>!t.disableSorting)),...o.filter((t=>t.disableSorting))]:o.sort(((t,e)=>t.disableSorting&&!e.disableSorting?-1:s(t.value,e.value)))})),this._allItems=(0,c.A)(((t,e,i)=>[...this._visibleItems(t,e,i),...this._hiddenItems(t,e)])),this._hiddenItems=(0,c.A)(((t,e)=>t.filter((t=>e.includes(t.value))))),this._maxSortableIndex=(0,c.A)(((t,e)=>t.filter((t=>!t.disableSorting&&!e.includes(t.value))).length-1)),this._keyActivatedMove=(t,e=!1)=>{const i=this._dragIndex;"ArrowUp"===t.key?this._dragIndex=Math.max(0,this._dragIndex-1):this._dragIndex=Math.min(this._maxSortableIndex(this.items,this.value.hidden),this._dragIndex+1),this._moveItem(i,this._dragIndex),setTimeout((async()=>{var t;await this.updateComplete;const i=null===(t=this.shadowRoot)||void 0===t?void 0:t.querySelector(`ha-md-list-item:nth-child(${this._dragIndex+1})`);null==i||i.focus(),e&&(this._dragIndex=null)}))},this._sortKeydown=t=>{null===this._dragIndex||"ArrowUp"!==t.key&&"ArrowDown"!==t.key?null!==this._dragIndex&&"Escape"===t.key&&(t.preventDefault(),t.stopPropagation(),this._dragIndex=null,this.removeEventListener("keydown",this._sortKeydown)):(t.preventDefault(),this._keyActivatedMove(t))},this._listElementKeydown=t=>{!t.altKey||"ArrowUp"!==t.key&&"ArrowDown"!==t.key?(!this.showNavigationButton&&"Enter"===t.key||" "===t.key)&&this._dragHandleKeydown(t):(t.preventDefault(),this._dragIndex=t.target.idx,this._keyActivatedMove(t,!0))}}}Z.styles=(0,a.AH)(f||(f=k`
    :host {
      display: block;
    }
    .handle {
      cursor: move;
      padding: 8px;
      margin: -8px;
    }
    .separator {
      width: 1px;
      background-color: var(--divider-color);
      height: 21px;
      margin: 0 -4px;
    }
    ha-md-list {
      padding: 0;
    }
    ha-md-list-item {
      --md-list-item-top-space: 0;
      --md-list-item-bottom-space: 0;
      --md-list-item-leading-space: 8px;
      --md-list-item-trailing-space: 8px;
      --md-list-item-two-line-container-height: 48px;
      --md-list-item-one-line-container-height: 48px;
    }
    ha-md-list-item.drag-selected {
      --md-focus-ring-color: rgba(var(--rgb-accent-color), 0.6);
      border-radius: 8px;
      outline: solid;
      outline-color: rgba(var(--rgb-accent-color), 0.6);
      outline-offset: -2px;
      outline-width: 2px;
      background-color: rgba(var(--rgb-accent-color), 0.08);
    }
    ha-md-list-item ha-icon-button {
      margin-left: -12px;
      margin-right: -12px;
    }
    ha-md-list-item.hidden {
      --md-list-item-label-text-color: var(--disabled-text-color);
      --md-list-item-supporting-text-color: var(--disabled-text-color);
    }
    ha-md-list-item.hidden .icon {
      color: var(--disabled-text-color);
    }
  `)),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],Z.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],Z.prototype,"items",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean,attribute:"show-navigation-button"})],Z.prototype,"showNavigationButton",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean,attribute:"dont-sort-visible"})],Z.prototype,"dontSortVisible",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],Z.prototype,"value",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],Z.prototype,"actionsRenderer",void 0),(0,s.__decorate)([(0,n.wk)()],Z.prototype,"_dragIndex",void 0),Z=(0,s.__decorate)([(0,n.EM)("ha-items-display-editor")],Z),e()}catch(g){e(g)}}))},26850:function(t,e,i){i.a(t,(async function(t,s){try{i.r(e),i.d(e,{HaAreasDisplaySelector:function(){return c}});i(35748),i(95013);var o=i(69868),a=i(84922),n=i(11991),d=i(85710),r=t([d]);d=(r.then?(await r)():r)[0];let l,h=t=>t;class c extends a.WF{render(){return(0,a.qy)(l||(l=h`
      <ha-areas-display-editor
        .hass=${0}
        .value=${0}
        .label=${0}
        .helper=${0}
        .disabled=${0}
        .required=${0}
      ></ha-areas-display-editor>
    `),this.hass,this.value,this.label,this.helper,this.disabled,this.required)}constructor(...t){super(...t),this.disabled=!1,this.required=!0}}(0,o.__decorate)([(0,n.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],c.prototype,"selector",void 0),(0,o.__decorate)([(0,n.MZ)()],c.prototype,"value",void 0),(0,o.__decorate)([(0,n.MZ)()],c.prototype,"label",void 0),(0,o.__decorate)([(0,n.MZ)()],c.prototype,"helper",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],c.prototype,"disabled",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],c.prototype,"required",void 0),c=(0,o.__decorate)([(0,n.EM)("ha-selector-areas_display")],c),s()}catch(l){s(l)}}))},88006:function(t,e,i){i.a(t,(async function(t,s){try{i.d(e,{P:function(){return d}});var o=i(30808),a=(i(35748),i(5934),i(88238),i(34536),i(16257),i(20152),i(44711),i(72108),i(77030),i(95013),i(19886)),n=t([o]);o=(n.then?(await n)():n)[0];class d{handleChanges(t){var e;this.value=null===(e=this.callback)||void 0===e?void 0:e.call(this,t,this.u)}hostConnected(){for(const t of this.t)this.observe(t)}hostDisconnected(){this.disconnect()}async hostUpdated(){!this.o&&this.i&&this.handleChanges([]),this.i=!1}observe(t){this.t.add(t),this.u.observe(t,this.l),this.i=!0,this.h.requestUpdate()}unobserve(t){this.t.delete(t),this.u.unobserve(t)}disconnect(){this.u.disconnect()}constructor(t,{target:e,config:i,callback:s,skipInitial:o}){this.t=new Set,this.o=!1,this.i=!1,this.h=t,null!==e&&this.t.add(null!=e?e:t),this.l=i,this.o=null!=o?o:this.o,this.callback=s,a.S||(window.ResizeObserver?(this.u=new ResizeObserver((t=>{this.handleChanges(t),this.h.requestUpdate()})),t.addController(this)):console.warn("ResizeController error: browser does not support ResizeObserver."))}}s()}catch(d){s(d)}}))},55:function(t,e,i){i.d(e,{T:function(){return u}});i(35748),i(65315),i(84136),i(5934),i(95013);var s=i(11681),o=i(67851),a=i(40594);i(32203),i(79392),i(46852);class n{disconnect(){this.G=void 0}reconnect(t){this.G=t}deref(){return this.G}constructor(t){this.G=t}}class d{get(){return this.Y}pause(){var t;null!==(t=this.Y)&&void 0!==t||(this.Y=new Promise((t=>this.Z=t)))}resume(){var t;null!==(t=this.Z)&&void 0!==t&&t.call(this),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var r=i(64363);const l=t=>!(0,o.sO)(t)&&"function"==typeof t.then,h=1073741823;class c extends a.Kq{render(...t){var e;return null!==(e=t.find((t=>!l(t))))&&void 0!==e?e:s.c0}update(t,e){const i=this._$Cbt;let o=i.length;this._$Cbt=e;const a=this._$CK,n=this._$CX;this.isConnected||this.disconnected();for(let s=0;s<e.length&&!(s>this._$Cwt);s++){const t=e[s];if(!l(t))return this._$Cwt=s,t;s<o&&t===i[s]||(this._$Cwt=h,o=0,Promise.resolve(t).then((async e=>{for(;n.get();)await n.get();const i=a.deref();if(void 0!==i){const s=i._$Cbt.indexOf(t);s>-1&&s<i._$Cwt&&(i._$Cwt=s,i.setValue(e))}})))}return s.c0}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=h,this._$Cbt=[],this._$CK=new n(this),this._$CX=new d}}const u=(0,r.u$)(c)}}]);
//# sourceMappingURL=5535.4c13d23898397928.js.map