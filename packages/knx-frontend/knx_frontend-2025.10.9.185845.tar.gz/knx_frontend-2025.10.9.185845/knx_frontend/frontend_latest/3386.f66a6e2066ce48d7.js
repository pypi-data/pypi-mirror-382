/*! For license information please see 3386.f66a6e2066ce48d7.js.LICENSE.txt */
export const __webpack_id__="3386";export const __webpack_ids__=["3386"];export const __webpack_modules__={75633:function(t,e,i){i.r(e),i.d(e,{HaAreasDisplaySelector:()=>x});var s=i(69868),o=i(84922),a=i(11991),n=i(73120),d=i(88340),r=i(18944),h=(i(99741),i(88006)),l=i(75907),c=i(13802),u=i(33055),p=i(60434),v=i(65940),_=i(20674),g=i(90963);i(81164),i(93672),i(72062),i(5803),i(98343),i(8115),i(95635);class m extends o.WF{render(){const t=this._allItems(this.items,this.value.hidden,this.value.order),e=this._showIcon.value;return o.qy`
      <ha-sortable
        draggable-selector=".draggable"
        handle-selector=".handle"
        @item-moved=${this._itemMoved}
      >
        <ha-md-list>
          ${(0,u.u)(t,(t=>t.value),((t,i)=>{const s=!this.value.hidden.includes(t.value),{label:a,value:n,description:d,icon:r,iconPath:h,disableSorting:u}=t;return o.qy`
                <ha-md-list-item
                  type="button"
                  @click=${this.showNavigationButton?this._navigate:void 0}
                  .value=${n}
                  class=${(0,l.H)({hidden:!s,draggable:s&&!u,"drag-selected":this._dragIndex===i})}
                  @keydown=${s&&!u?this._listElementKeydown:void 0}
                  .idx=${i}
                >
                  <span slot="headline">${a}</span>
                  ${d?o.qy`<span slot="supporting-text">${d}</span>`:o.s6}
                  ${e?r?o.qy`
                          <ha-icon
                            class="icon"
                            .icon=${(0,p.T)(r,"")}
                            slot="start"
                          ></ha-icon>
                        `:h?o.qy`
                            <ha-svg-icon
                              class="icon"
                              .path=${h}
                              slot="start"
                            ></ha-svg-icon>
                          `:o.s6:o.s6}
                  ${this.showNavigationButton?o.qy`
                        <ha-icon-next slot="end"></ha-icon-next>
                        <div slot="end" class="separator"></div>
                      `:o.s6}
                  ${this.actionsRenderer?o.qy`
                        <div slot="end" @click=${_.d}>
                          ${this.actionsRenderer(t)}
                        </div>
                      `:o.s6}
                  <ha-icon-button
                    .path=${s?"M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z":"M11.83,9L15,12.16C15,12.11 15,12.05 15,12A3,3 0 0,0 12,9C11.94,9 11.89,9 11.83,9M7.53,9.8L9.08,11.35C9.03,11.56 9,11.77 9,12A3,3 0 0,0 12,15C12.22,15 12.44,14.97 12.65,14.92L14.2,16.47C13.53,16.8 12.79,17 12,17A5,5 0 0,1 7,12C7,11.21 7.2,10.47 7.53,9.8M2,4.27L4.28,6.55L4.73,7C3.08,8.3 1.78,10 1,12C2.73,16.39 7,19.5 12,19.5C13.55,19.5 15.03,19.2 16.38,18.66L16.81,19.08L19.73,22L21,20.73L3.27,3M12,7A5,5 0 0,1 17,12C17,12.64 16.87,13.26 16.64,13.82L19.57,16.75C21.07,15.5 22.27,13.86 23,12C21.27,7.61 17,4.5 12,4.5C10.6,4.5 9.26,4.75 8,5.2L10.17,7.35C10.74,7.13 11.35,7 12,7Z"}
                    slot="end"
                    .label=${this.hass.localize("ui.components.items-display-editor."+(s?"hide":"show"),{label:a})}
                    .value=${n}
                    @click=${this._toggle}
                  ></ha-icon-button>
                  ${s&&!u?o.qy`
                        <ha-svg-icon
                          tabindex=${(0,c.J)(this.showNavigationButton?"0":void 0)}
                          .idx=${i}
                          @keydown=${this.showNavigationButton?this._dragHandleKeydown:void 0}
                          class="handle"
                          .path=${"M7,19V17H9V19H7M11,19V17H13V19H11M15,19V17H17V19H15M7,15V13H9V15H7M11,15V13H13V15H11M15,15V13H17V15H15M7,11V9H9V11H7M11,11V9H13V11H11M15,11V9H17V11H15M7,7V5H9V7H7M11,7V5H13V7H11M15,7V5H17V7H15Z"}
                          slot="end"
                        ></ha-svg-icon>
                      `:o.qy`<ha-svg-icon slot="end"></ha-svg-icon>`}
                </ha-md-list-item>
              `}))}
        </ha-md-list>
      </ha-sortable>
    `}_toggle(t){t.stopPropagation(),this._dragIndex=null;const e=t.currentTarget.value,i=this._hiddenItems(this.items,this.value.hidden).map((t=>t.value));i.includes(e)?i.splice(i.indexOf(e),1):i.push(e);const s=this._visibleItems(this.items,i,this.value.order).map((t=>t.value));this.value={hidden:i,order:s},(0,n.r)(this,"value-changed",{value:this.value})}_itemMoved(t){t.stopPropagation();const{oldIndex:e,newIndex:i}=t.detail;this._moveItem(e,i)}_moveItem(t,e){if(t===e)return;const i=this._visibleItems(this.items,this.value.hidden,this.value.order).map((t=>t.value)),s=i.splice(t,1)[0];i.splice(e,0,s),this.value={...this.value,order:i},(0,n.r)(this,"value-changed",{value:this.value})}_navigate(t){const e=t.currentTarget.value;(0,n.r)(this,"item-display-navigate-clicked",{value:e}),t.stopPropagation()}_dragHandleKeydown(t){"Enter"!==t.key&&" "!==t.key||(t.preventDefault(),t.stopPropagation(),null===this._dragIndex?(this._dragIndex=t.target.idx,this.addEventListener("keydown",this._sortKeydown)):(this.removeEventListener("keydown",this._sortKeydown),this._dragIndex=null))}disconnectedCallback(){super.disconnectedCallback(),this.removeEventListener("keydown",this._sortKeydown)}constructor(...t){super(...t),this.items=[],this.showNavigationButton=!1,this.dontSortVisible=!1,this.value={order:[],hidden:[]},this._dragIndex=null,this._showIcon=new h.P(this,{callback:t=>t[0]?.contentRect.width>450}),this._visibleItems=(0,v.A)(((t,e,i)=>{const s=(0,g.u1)(i),o=t.filter((t=>!e.includes(t.value)));return this.dontSortVisible?[...o.filter((t=>!t.disableSorting)),...o.filter((t=>t.disableSorting))]:o.sort(((t,e)=>t.disableSorting&&!e.disableSorting?-1:s(t.value,e.value)))})),this._allItems=(0,v.A)(((t,e,i)=>[...this._visibleItems(t,e,i),...this._hiddenItems(t,e)])),this._hiddenItems=(0,v.A)(((t,e)=>t.filter((t=>e.includes(t.value))))),this._maxSortableIndex=(0,v.A)(((t,e)=>t.filter((t=>!t.disableSorting&&!e.includes(t.value))).length-1)),this._keyActivatedMove=(t,e=!1)=>{const i=this._dragIndex;"ArrowUp"===t.key?this._dragIndex=Math.max(0,this._dragIndex-1):this._dragIndex=Math.min(this._maxSortableIndex(this.items,this.value.hidden),this._dragIndex+1),this._moveItem(i,this._dragIndex),setTimeout((async()=>{await this.updateComplete;const t=this.shadowRoot?.querySelector(`ha-md-list-item:nth-child(${this._dragIndex+1})`);t?.focus(),e&&(this._dragIndex=null)}))},this._sortKeydown=t=>{null===this._dragIndex||"ArrowUp"!==t.key&&"ArrowDown"!==t.key?null!==this._dragIndex&&"Escape"===t.key&&(t.preventDefault(),t.stopPropagation(),this._dragIndex=null,this.removeEventListener("keydown",this._sortKeydown)):(t.preventDefault(),this._keyActivatedMove(t))},this._listElementKeydown=t=>{!t.altKey||"ArrowUp"!==t.key&&"ArrowDown"!==t.key?(!this.showNavigationButton&&"Enter"===t.key||" "===t.key)&&this._dragHandleKeydown(t):(t.preventDefault(),this._dragIndex=t.target.idx,this._keyActivatedMove(t,!0))}}}m.styles=o.AH`
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
  `,(0,s.__decorate)([(0,a.MZ)({attribute:!1})],m.prototype,"hass",void 0),(0,s.__decorate)([(0,a.MZ)({attribute:!1})],m.prototype,"items",void 0),(0,s.__decorate)([(0,a.MZ)({type:Boolean,attribute:"show-navigation-button"})],m.prototype,"showNavigationButton",void 0),(0,s.__decorate)([(0,a.MZ)({type:Boolean,attribute:"dont-sort-visible"})],m.prototype,"dontSortVisible",void 0),(0,s.__decorate)([(0,a.MZ)({attribute:!1})],m.prototype,"value",void 0),(0,s.__decorate)([(0,a.MZ)({attribute:!1})],m.prototype,"actionsRenderer",void 0),(0,s.__decorate)([(0,a.wk)()],m.prototype,"_dragIndex",void 0),m=(0,s.__decorate)([(0,a.EM)("ha-items-display-editor")],m);i(11934);const b="M20 2H4C2.9 2 2 2.9 2 4V20C2 21.11 2.9 22 4 22H20C21.11 22 22 21.11 22 20V4C22 2.9 21.11 2 20 2M4 6L6 4H10.9L4 10.9V6M4 13.7L13.7 4H18.6L4 18.6V13.7M20 18L18 20H13.1L20 13.1V18M20 10.3L10.3 20H5.4L20 5.4V10.3Z";class y extends o.WF{render(){const t=(0,r.dj)(this.hass.areas),e=Object.values(this.hass.areas).sort(((e,i)=>t(e.area_id,i.area_id))).map((t=>{const{floor:e}=(0,d.L)(t,this.hass);return{value:t.area_id,label:t.name,icon:t.icon??void 0,iconPath:b,description:e?.name}})),i={order:this.value?.order??[],hidden:this.value?.hidden??[]};return o.qy`
      <ha-expansion-panel
        outlined
        .header=${this.label}
        .expanded=${this.expanded}
      >
        <ha-svg-icon slot="leading-icon" .path=${b}></ha-svg-icon>
        <ha-items-display-editor
          .hass=${this.hass}
          .items=${e}
          .value=${i}
          @value-changed=${this._areaDisplayChanged}
          .showNavigationButton=${this.showNavigationButton}
        ></ha-items-display-editor>
      </ha-expansion-panel>
    `}async _areaDisplayChanged(t){t.stopPropagation();const e=t.detail.value,i={...this.value,...e};0===i.hidden?.length&&delete i.hidden,0===i.order?.length&&delete i.order,(0,n.r)(this,"value-changed",{value:i})}constructor(...t){super(...t),this.expanded=!1,this.disabled=!1,this.required=!1,this.showNavigationButton=!1}}(0,s.__decorate)([(0,a.MZ)({attribute:!1})],y.prototype,"hass",void 0),(0,s.__decorate)([(0,a.MZ)()],y.prototype,"label",void 0),(0,s.__decorate)([(0,a.MZ)({attribute:!1})],y.prototype,"value",void 0),(0,s.__decorate)([(0,a.MZ)()],y.prototype,"helper",void 0),(0,s.__decorate)([(0,a.MZ)({type:Boolean})],y.prototype,"expanded",void 0),(0,s.__decorate)([(0,a.MZ)({type:Boolean})],y.prototype,"disabled",void 0),(0,s.__decorate)([(0,a.MZ)({type:Boolean})],y.prototype,"required",void 0),(0,s.__decorate)([(0,a.MZ)({type:Boolean,attribute:"show-navigation-button"})],y.prototype,"showNavigationButton",void 0),y=(0,s.__decorate)([(0,a.EM)("ha-areas-display-editor")],y);class x extends o.WF{render(){return o.qy`
      <ha-areas-display-editor
        .hass=${this.hass}
        .value=${this.value}
        .label=${this.label}
        .helper=${this.helper}
        .disabled=${this.disabled}
        .required=${this.required}
      ></ha-areas-display-editor>
    `}constructor(...t){super(...t),this.disabled=!1,this.required=!0}}(0,s.__decorate)([(0,a.MZ)({attribute:!1})],x.prototype,"hass",void 0),(0,s.__decorate)([(0,a.MZ)({attribute:!1})],x.prototype,"selector",void 0),(0,s.__decorate)([(0,a.MZ)()],x.prototype,"value",void 0),(0,s.__decorate)([(0,a.MZ)()],x.prototype,"label",void 0),(0,s.__decorate)([(0,a.MZ)()],x.prototype,"helper",void 0),(0,s.__decorate)([(0,a.MZ)({type:Boolean})],x.prototype,"disabled",void 0),(0,s.__decorate)([(0,a.MZ)({type:Boolean})],x.prototype,"required",void 0),x=(0,s.__decorate)([(0,a.EM)("ha-selector-areas_display")],x)},88006:function(t,e,i){i.d(e,{P:()=>o});var s=i(19886);class o{handleChanges(t){this.value=this.callback?.(t,this.u)}hostConnected(){for(const t of this.t)this.observe(t)}hostDisconnected(){this.disconnect()}async hostUpdated(){!this.o&&this.i&&this.handleChanges([]),this.i=!1}observe(t){this.t.add(t),this.u.observe(t,this.l),this.i=!0,this.h.requestUpdate()}unobserve(t){this.t.delete(t),this.u.unobserve(t)}disconnect(){this.u.disconnect()}constructor(t,{target:e,config:i,callback:o,skipInitial:a}){this.t=new Set,this.o=!1,this.i=!1,this.h=t,null!==e&&this.t.add(e??t),this.l=i,this.o=a??this.o,this.callback=o,s.S||(window.ResizeObserver?(this.u=new ResizeObserver((t=>{this.handleChanges(t),this.h.requestUpdate()})),t.addController(this)):console.warn("ResizeController error: browser does not support ResizeObserver."))}}},60434:function(t,e,i){i.d(e,{T:()=>u});var s=i(11681),o=i(67851),a=i(40594);class n{disconnect(){this.G=void 0}reconnect(t){this.G=t}deref(){return this.G}constructor(t){this.G=t}}class d{get(){return this.Y}pause(){this.Y??=new Promise((t=>this.Z=t))}resume(){this.Z?.(),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var r=i(64363);const h=t=>!(0,o.sO)(t)&&"function"==typeof t.then,l=1073741823;class c extends a.Kq{render(...t){return t.find((t=>!h(t)))??s.c0}update(t,e){const i=this._$Cbt;let o=i.length;this._$Cbt=e;const a=this._$CK,n=this._$CX;this.isConnected||this.disconnected();for(let s=0;s<e.length&&!(s>this._$Cwt);s++){const t=e[s];if(!h(t))return this._$Cwt=s,t;s<o&&t===i[s]||(this._$Cwt=l,o=0,Promise.resolve(t).then((async e=>{for(;n.get();)await n.get();const i=a.deref();if(void 0!==i){const s=i._$Cbt.indexOf(t);s>-1&&s<i._$Cwt&&(i._$Cwt=s,i.setValue(e))}})))}return s.c0}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=l,this._$Cbt=[],this._$CK=new n(this),this._$CX=new d}}const u=(0,r.u$)(c)}};
//# sourceMappingURL=3386.f66a6e2066ce48d7.js.map