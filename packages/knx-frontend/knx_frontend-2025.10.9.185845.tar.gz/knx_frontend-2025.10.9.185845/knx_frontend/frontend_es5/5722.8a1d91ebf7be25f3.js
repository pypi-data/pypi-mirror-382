"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["5722"],{895:function(e,t,a){a.a(e,(async function(e,r){try{a.d(t,{PE:function(){return c}});a(79827);var o=a(96904),i=a(6423),n=a(95075),s=e([o]);o=(s.then?(await s)():s)[0];const l=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"],c=e=>e.first_weekday===n.zt.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(e.language).weekInfo.firstDay%7:(0,i.S)(e.language)%7:l.includes(e.first_weekday)?l.indexOf(e.first_weekday):1;r()}catch(l){r(l)}}))},45980:function(e,t,a){a.a(e,(async function(e,r){try{a.d(t,{K:function(){return c}});var o=a(96904),i=a(65940),n=a(83516),s=e([o,n]);[o,n]=s.then?(await s)():s;const l=(0,i.A)((e=>new Intl.RelativeTimeFormat(e.language,{numeric:"auto"}))),c=(e,t,a,r=!0)=>{const o=(0,n.x)(e,a,t);return r?l(t).format(o.value,o.unit):Intl.NumberFormat(t.language,{style:"unit",unit:o.unit,unitDisplay:"long"}).format(Math.abs(o.value))};r()}catch(l){r(l)}}))},83516:function(e,t,a){a.a(e,(async function(e,r){try{a.d(t,{x:function(){return u}});a(12977);var o=a(41484),i=a(88258),n=a(39826),s=a(895),l=e([s]);s=(l.then?(await l)():l)[0];const d=1e3,h=60,p=60*h;function u(e,t=Date.now(),a,r={}){const l=Object.assign(Object.assign({},g),r||{}),c=(+e-+t)/d;if(Math.abs(c)<l.second)return{value:Math.round(c),unit:"second"};const u=c/h;if(Math.abs(u)<l.minute)return{value:Math.round(u),unit:"minute"};const b=c/p;if(Math.abs(b)<l.hour)return{value:Math.round(b),unit:"hour"};const v=new Date(e),y=new Date(t);v.setHours(0,0,0,0),y.setHours(0,0,0,0);const m=(0,o.c)(v,y);if(0===m)return{value:Math.round(b),unit:"hour"};if(Math.abs(m)<l.day)return{value:m,unit:"day"};const _=(0,s.PE)(a),f=(0,i.k)(v,{weekStartsOn:_}),x=(0,i.k)(y,{weekStartsOn:_}),w=(0,n.I)(f,x);if(0===w)return{value:m,unit:"day"};if(Math.abs(w)<l.week)return{value:w,unit:"week"};const k=v.getFullYear()-y.getFullYear(),$=12*k+v.getMonth()-y.getMonth();return 0===$?{value:w,unit:"week"}:Math.abs($)<l.month||0===k?{value:$,unit:"month"}:{value:Math.round(k),unit:"year"}}const g={second:45,minute:45,hour:22,day:5,week:4,month:11};r()}catch(c){r(c)}}))},23749:function(e,t,a){a.r(t);a(35748),a(95013);var r=a(69868),o=a(84922),i=a(11991),n=a(75907),s=a(73120);a(93672),a(95635);let l,c,d,h,p=e=>e;const u={info:"M11,9H13V7H11M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,17H13V11H11V17Z",warning:"M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16",error:"M11,15H13V17H11V15M11,7H13V13H11V7M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20Z",success:"M20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4C12.76,4 13.5,4.11 14.2,4.31L15.77,2.74C14.61,2.26 13.34,2 12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12M7.91,10.08L6.5,11.5L11,16L21,6L19.59,4.58L11,13.17L7.91,10.08Z"};class g extends o.WF{render(){return(0,o.qy)(l||(l=p`
      <div
        class="issue-type ${0}"
        role="alert"
      >
        <div class="icon ${0}">
          <slot name="icon">
            <ha-svg-icon .path=${0}></ha-svg-icon>
          </slot>
        </div>
        <div class=${0}>
          <div class="main-content">
            ${0}
            <slot></slot>
          </div>
          <div class="action">
            <slot name="action">
              ${0}
            </slot>
          </div>
        </div>
      </div>
    `),(0,n.H)({[this.alertType]:!0}),this.title?"":"no-title",u[this.alertType],(0,n.H)({content:!0,narrow:this.narrow}),this.title?(0,o.qy)(c||(c=p`<div class="title">${0}</div>`),this.title):o.s6,this.dismissable?(0,o.qy)(d||(d=p`<ha-icon-button
                    @click=${0}
                    label="Dismiss alert"
                    .path=${0}
                  ></ha-icon-button>`),this._dismissClicked,"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"):o.s6)}_dismissClicked(){(0,s.r)(this,"alert-dismissed-clicked")}constructor(...e){super(...e),this.title="",this.alertType="info",this.dismissable=!1,this.narrow=!1}}g.styles=(0,o.AH)(h||(h=p`
    .issue-type {
      position: relative;
      padding: 8px;
      display: flex;
    }
    .icon {
      height: var(--ha-alert-icon-size, 24px);
      width: var(--ha-alert-icon-size, 24px);
    }
    .issue-type::after {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      opacity: 0.12;
      pointer-events: none;
      content: "";
      border-radius: 4px;
    }
    .icon.no-title {
      align-self: center;
    }
    .content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      text-align: var(--float-start);
    }
    .content.narrow {
      flex-direction: column;
      align-items: flex-end;
    }
    .action {
      z-index: 1;
      width: min-content;
      --mdc-theme-primary: var(--primary-text-color);
    }
    .main-content {
      overflow-wrap: anywhere;
      word-break: break-word;
      line-height: normal;
      margin-left: 8px;
      margin-right: 0;
      margin-inline-start: 8px;
      margin-inline-end: 8px;
    }
    .title {
      margin-top: 2px;
      font-weight: var(--ha-font-weight-bold);
    }
    .action ha-icon-button {
      --mdc-theme-primary: var(--primary-text-color);
      --mdc-icon-button-size: 36px;
    }
    .issue-type.info > .icon {
      color: var(--info-color);
    }
    .issue-type.info::after {
      background-color: var(--info-color);
    }

    .issue-type.warning > .icon {
      color: var(--warning-color);
    }
    .issue-type.warning::after {
      background-color: var(--warning-color);
    }

    .issue-type.error > .icon {
      color: var(--error-color);
    }
    .issue-type.error::after {
      background-color: var(--error-color);
    }

    .issue-type.success > .icon {
      color: var(--success-color);
    }
    .issue-type.success::after {
      background-color: var(--success-color);
    }
    :host ::slotted(ul) {
      margin: 0;
      padding-inline-start: 20px;
    }
  `)),(0,r.__decorate)([(0,i.MZ)()],g.prototype,"title",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:"alert-type"})],g.prototype,"alertType",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean})],g.prototype,"dismissable",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean})],g.prototype,"narrow",void 0),g=(0,r.__decorate)([(0,i.EM)("ha-alert")],g)},86853:function(e,t,a){a(35748),a(95013);var r=a(69868),o=a(84922),i=a(11991);let n,s,l,c=e=>e;class d extends o.WF{render(){return(0,o.qy)(n||(n=c`
      ${0}
      <slot></slot>
    `),this.header?(0,o.qy)(s||(s=c`<h1 class="card-header">${0}</h1>`),this.header):o.s6)}constructor(...e){super(...e),this.raised=!1}}d.styles=(0,o.AH)(l||(l=c`
    :host {
      background: var(
        --ha-card-background,
        var(--card-background-color, white)
      );
      -webkit-backdrop-filter: var(--ha-card-backdrop-filter, none);
      backdrop-filter: var(--ha-card-backdrop-filter, none);
      box-shadow: var(--ha-card-box-shadow, none);
      box-sizing: border-box;
      border-radius: var(--ha-card-border-radius, 12px);
      border-width: var(--ha-card-border-width, 1px);
      border-style: solid;
      border-color: var(--ha-card-border-color, var(--divider-color, #e0e0e0));
      color: var(--primary-text-color);
      display: block;
      transition: all 0.3s ease-out;
      position: relative;
    }

    :host([raised]) {
      border: none;
      box-shadow: var(
        --ha-card-box-shadow,
        0px 2px 1px -1px rgba(0, 0, 0, 0.2),
        0px 1px 1px 0px rgba(0, 0, 0, 0.14),
        0px 1px 3px 0px rgba(0, 0, 0, 0.12)
      );
    }

    .card-header,
    :host ::slotted(.card-header) {
      color: var(--ha-card-header-color, var(--primary-text-color));
      font-family: var(--ha-card-header-font-family, inherit);
      font-size: var(--ha-card-header-font-size, var(--ha-font-size-2xl));
      letter-spacing: -0.012em;
      line-height: var(--ha-line-height-expanded);
      padding: 12px 16px 16px;
      display: block;
      margin-block-start: 0px;
      margin-block-end: 0px;
      font-weight: var(--ha-font-weight-normal);
    }

    :host ::slotted(.card-content:not(:first-child)),
    slot:not(:first-child)::slotted(.card-content) {
      padding-top: 0px;
      margin-top: -8px;
    }

    :host ::slotted(.card-content) {
      padding: 16px;
    }

    :host ::slotted(.card-actions) {
      border-top: 1px solid var(--divider-color, #e8e8e8);
      padding: 8px;
    }
  `)),(0,r.__decorate)([(0,i.MZ)()],d.prototype,"header",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean,reflect:!0})],d.prototype,"raised",void 0),d=(0,r.__decorate)([(0,i.EM)("ha-card")],d)},35881:function(e,t,a){a.a(e,(async function(e,r){try{a.r(t),a.d(t,{HaIconOverflowMenu:function(){return x}});a(35748),a(65315),a(37089),a(95013);var o=a(69868),i=a(84922),n=a(11991),s=a(75907),l=a(83566),c=(a(61647),a(93672),a(95635),a(89652)),d=(a(70154),a(90666),e([c]));c=(d.then?(await d)():d)[0];let h,p,u,g,b,v,y,m,_=e=>e;const f="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z";class x extends i.WF{render(){return(0,i.qy)(h||(h=_`
      ${0}
    `),this.narrow?(0,i.qy)(p||(p=_` <!-- Collapsed representation for small screens -->
            <ha-md-button-menu
              @click=${0}
              positioning="popover"
            >
              <ha-icon-button
                .label=${0}
                .path=${0}
                slot="trigger"
              ></ha-icon-button>

              ${0}
            </ha-md-button-menu>`),this._handleIconOverflowMenuOpened,this.hass.localize("ui.common.overflow_menu"),f,this.items.map((e=>e.divider?(0,i.qy)(u||(u=_`<ha-md-divider
                      role="separator"
                      tabindex="-1"
                    ></ha-md-divider>`)):(0,i.qy)(g||(g=_`<ha-md-menu-item
                      ?disabled=${0}
                      .clickAction=${0}
                      class=${0}
                    >
                      <ha-svg-icon
                        slot="start"
                        class=${0}
                        .path=${0}
                      ></ha-svg-icon>
                      ${0}
                    </ha-md-menu-item> `),e.disabled,e.action,(0,s.H)({warning:Boolean(e.warning)}),(0,s.H)({warning:Boolean(e.warning)}),e.path,e.label)))):(0,i.qy)(b||(b=_`
            <!-- Icon representation for big screens -->
            ${0}
          `),this.items.map((e=>{var t;return e.narrowOnly?i.s6:e.divider?(0,i.qy)(v||(v=_`<div role="separator"></div>`)):(0,i.qy)(y||(y=_`<ha-tooltip
                        .disabled=${0}
                        .for="icon-button-${0}"
                        >${0} </ha-tooltip
                      ><ha-icon-button
                        .id="icon-button-${0}"
                        @click=${0}
                        .label=${0}
                        .path=${0}
                        ?disabled=${0}
                      ></ha-icon-button> `),!e.tooltip,e.label,null!==(t=e.tooltip)&&void 0!==t?t:"",e.label,e.action,e.label,e.path,e.disabled)}))))}_handleIconOverflowMenuOpened(e){e.stopPropagation()}static get styles(){return[l.RF,(0,i.AH)(m||(m=_`
        :host {
          display: flex;
          justify-content: flex-end;
        }
        div[role="separator"] {
          border-right: 1px solid var(--divider-color);
          width: 1px;
        }
      `))]}constructor(...e){super(...e),this.items=[],this.narrow=!1}}(0,o.__decorate)([(0,n.MZ)({attribute:!1})],x.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)({type:Array})],x.prototype,"items",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],x.prototype,"narrow",void 0),x=(0,o.__decorate)([(0,n.EM)("ha-icon-overflow-menu")],x),r()}catch(h){r(h)}}))},89652:function(e,t,a){a.a(e,(async function(e,t){try{a(35748),a(95013);var r=a(69868),o=a(28784),i=a(84922),n=a(11991),s=e([o]);o=(s.then?(await s)():s)[0];let l,c=e=>e;class d extends o.A{static get styles(){return[o.A.styles,(0,i.AH)(l||(l=c`
        :host {
          --wa-tooltip-background-color: var(--secondary-background-color);
          --wa-tooltip-color: var(--primary-text-color);
          --wa-tooltip-font-family: var(
            --ha-tooltip-font-family,
            var(--ha-font-family-body)
          );
          --wa-tooltip-font-size: var(
            --ha-tooltip-font-size,
            var(--ha-font-size-s)
          );
          --wa-tooltip-font-weight: var(
            --ha-tooltip-font-weight,
            var(--ha-font-weight-normal)
          );
          --wa-tooltip-line-height: var(
            --ha-tooltip-line-height,
            var(--ha-line-height-condensed)
          );
          --wa-tooltip-padding: 8px;
          --wa-tooltip-border-radius: var(--ha-tooltip-border-radius, 4px);
          --wa-tooltip-arrow-size: var(--ha-tooltip-arrow-size, 8px);
          --wa-z-index-tooltip: var(--ha-tooltip-z-index, 1000);
        }
      `))]}constructor(...e){super(...e),this.showDelay=150,this.hideDelay=400}}(0,r.__decorate)([(0,n.MZ)({attribute:"show-delay",type:Number})],d.prototype,"showDelay",void 0),(0,r.__decorate)([(0,n.MZ)({attribute:"hide-delay",type:Number})],d.prototype,"hideDelay",void 0),d=(0,r.__decorate)([(0,n.EM)("ha-tooltip")],d),t()}catch(l){t(l)}}))},99478:function(e,t,a){a(35748),a(9724),a(65315),a(22416),a(37089),a(48169),a(95013);var r=a(69868),o=a(84922),i=a(11991),n=a(75907),s=a(73120),l=a(92095);let c,d,h,p,u,g,b=e=>e;const v=new l.Q("knx-project-tree-view");class y extends o.WF{connectedCallback(){super.connectedCallback();const e=t=>{Object.entries(t).forEach((([t,a])=>{a.group_addresses.length>0&&(this._selectableRanges[t]={selected:!1,groupAddresses:a.group_addresses}),e(a.group_ranges)}))};e(this.data.group_ranges),v.debug("ranges",this._selectableRanges)}render(){return(0,o.qy)(c||(c=b`<div class="ha-tree-view">${0}</div>`),this._recurseData(this.data.group_ranges))}_recurseData(e,t=0){const a=Object.entries(e).map((([e,a])=>{const r=Object.keys(a.group_ranges).length>0;if(!(r||a.group_addresses.length>0))return o.s6;const i=e in this._selectableRanges,s=!!i&&this._selectableRanges[e].selected,l={"range-item":!0,"root-range":0===t,"sub-range":t>0,selectable:i,"selected-range":s,"non-selected-range":i&&!s},c=(0,o.qy)(d||(d=b`<div
        class=${0}
        toggle-range=${0}
        @click=${0}
      >
        <span class="range-key">${0}</span>
        <span class="range-text">${0}</span>
      </div>`),(0,n.H)(l),i?e:o.s6,i?this.multiselect?this._selectionChangedMulti:this._selectionChangedSingle:o.s6,e,a.name);if(r){const e={"root-group":0===t,"sub-group":0!==t};return(0,o.qy)(h||(h=b`<div class=${0}>
          ${0} ${0}
        </div>`),(0,n.H)(e),c,this._recurseData(a.group_ranges,t+1))}return(0,o.qy)(p||(p=b`${0}`),c)}));return(0,o.qy)(u||(u=b`${0}`),a)}_selectionChangedMulti(e){const t=e.target.getAttribute("toggle-range");this._selectableRanges[t].selected=!this._selectableRanges[t].selected,this._selectionUpdate(),this.requestUpdate()}_selectionChangedSingle(e){const t=e.target.getAttribute("toggle-range"),a=this._selectableRanges[t].selected;Object.values(this._selectableRanges).forEach((e=>{e.selected=!1})),this._selectableRanges[t].selected=!a,this._selectionUpdate(),this.requestUpdate()}_selectionUpdate(){const e=Object.values(this._selectableRanges).reduce(((e,t)=>t.selected?e.concat(t.groupAddresses):e),[]);v.debug("selection changed",e),(0,s.r)(this,"knx-group-range-selection-changed",{groupAddresses:e})}constructor(...e){super(...e),this.multiselect=!1,this._selectableRanges={}}}y.styles=(0,o.AH)(g||(g=b`
    :host {
      margin: 0;
      height: 100%;
      overflow-y: scroll;
      overflow-x: hidden;
      background-color: var(--card-background-color);
    }

    .ha-tree-view {
      cursor: default;
    }

    .root-group {
      margin-bottom: 8px;
    }

    .root-group > * {
      padding-top: 5px;
      padding-bottom: 5px;
    }

    .range-item {
      display: block;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      font-size: 0.875rem;
    }

    .range-item > * {
      vertical-align: middle;
      pointer-events: none;
    }

    .range-key {
      color: var(--text-primary-color);
      font-size: 0.75rem;
      font-weight: 700;
      background-color: var(--label-badge-grey);
      border-radius: 4px;
      padding: 1px 4px;
      margin-right: 2px;
    }

    .root-range {
      padding-left: 8px;
      font-weight: 500;
      background-color: var(--secondary-background-color);

      & .range-key {
        color: var(--primary-text-color);
        background-color: var(--card-background-color);
      }
    }

    .sub-range {
      padding-left: 13px;
    }

    .selectable {
      cursor: pointer;
    }

    .selectable:hover {
      background-color: rgba(var(--rgb-primary-text-color), 0.04);
    }

    .selected-range {
      background-color: rgba(var(--rgb-primary-color), 0.12);

      & .range-key {
        background-color: var(--primary-color);
      }
    }

    .selected-range:hover {
      background-color: rgba(var(--rgb-primary-color), 0.07);
    }

    .non-selected-range {
      background-color: var(--card-background-color);
    }
  `)),(0,r.__decorate)([(0,i.MZ)({attribute:!1})],y.prototype,"data",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:!1})],y.prototype,"multiselect",void 0),(0,r.__decorate)([(0,i.wk)()],y.prototype,"_selectableRanges",void 0),y=(0,r.__decorate)([(0,i.EM)("knx-project-tree-view")],y)},93060:function(e,t,a){a.d(t,{CY:function(){return l},HF:function(){return s},RL:function(){return v},Vt:function(){return i},Zc:function(){return n},e4:function(){return o},u_:function(){return b}});a(9724),a(65315),a(48169),a(67579),a(47849),a(1485);var r=a(90227);const o={payload:e=>null==e.payload?"":Array.isArray(e.payload)?e.payload.reduce(((e,t)=>e+t.toString(16).padStart(2,"0")),"0x"):e.payload.toString(),valueWithUnit:e=>null==e.value?"":"number"==typeof e.value||"boolean"==typeof e.value||"string"==typeof e.value?e.value.toString()+(e.unit?" "+e.unit:""):(0,r.Bh)(e.value),timeWithMilliseconds:e=>new Date(e.timestamp).toLocaleTimeString(["en-US"],{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),dateWithMilliseconds:e=>new Date(e.timestamp).toLocaleTimeString([],{year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),dptNumber:e=>null==e.dpt_main?"":null==e.dpt_sub?e.dpt_main.toString():e.dpt_main.toString()+"."+e.dpt_sub.toString().padStart(3,"0"),dptNameNumber:e=>{const t=o.dptNumber(e);return null==e.dpt_name?`DPT ${t}`:t?`DPT ${t} ${e.dpt_name}`:e.dpt_name}},i=e=>null==e?"":e.main+(e.sub?"."+e.sub.toString().padStart(3,"0"):""),n=e=>e.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),s=e=>e.toLocaleDateString(void 0,{year:"numeric",month:"2-digit",day:"2-digit"})+", "+e.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),l=e=>{const t=new Date(e),a=e.match(/\.(\d{6})/),r=a?a[1]:"000000";return t.toLocaleDateString(void 0,{year:"numeric",month:"2-digit",day:"2-digit"})+", "+t.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit"})+"."+r},c=1e3,d=1e3,h=60*d,p=60*h,u=2,g=3;function b(e){const t=e.indexOf(".");if(-1===t)return 1e3*Date.parse(e);let a=e.indexOf("Z",t);-1===a&&(a=e.indexOf("+",t),-1===a&&(a=e.indexOf("-",t))),-1===a&&(a=e.length);const r=e.slice(0,t)+e.slice(a),o=Date.parse(r);let i=e.slice(t+1,a);return i.length<6?i=i.padEnd(6,"0"):i.length>6&&(i=i.slice(0,6)),1e3*o+Number(i)}function v(e,t="milliseconds"){if(null==e)return"—";const a=e<0?"-":"",r=Math.abs(e),o="milliseconds"===t?Math.round(r/c):Math.floor(r/c),i="microseconds"===t?r%c:0,n=Math.floor(o/p),s=Math.floor(o%p/h),l=Math.floor(o%h/d),b=o%d,v=e=>e.toString().padStart(u,"0"),y=e=>e.toString().padStart(g,"0"),m="microseconds"===t?`.${y(b)}${y(i)}`:`.${y(b)}`,_=`${v(s)}:${v(l)}`;return`${a}${n>0?`${v(n)}:${_}`:_}${m}`}},65857:function(e,t,a){a.a(e,(async function(e,r){try{a.r(t),a.d(t,{KNXProjectView:function(){return T}});a(79827),a(35748),a(99342),a(9724),a(65315),a(48169),a(12977),a(5934),a(47849),a(18223),a(95013);var o=a(69868),i=a(84922),n=a(11991),s=a(68476),l=a(65940),c=a(68985),d=a(92491),h=(a(54885),a(23749),a(86853),a(93672),a(35881)),p=(a(21339),a(45980)),u=(a(99478),a(22288)),g=a(49432),b=a(92095),v=a(93060),y=e([d,h,p]);[d,h,p]=y.then?(await y)():y;let m,_,f,x,w,k,$,M,A,H,j,S,V,L,q,z=e=>e;const D="M6,13H18V11H6M3,6V8H21V6M10,18H14V16H10V18Z",C="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",Z="M18 7C16.9 7 16 7.9 16 9V15C16 16.1 16.9 17 18 17H20C21.1 17 22 16.1 22 15V11H20V15H18V9H22V7H18M2 7V17H8V15H4V7H2M11 7C9.9 7 9 7.9 9 9V15C9 16.1 9.9 17 11 17H13C14.1 17 15 16.1 15 15V9C15 7.9 14.1 7 13 7H11M11 9H13V15H11V9Z",O=new b.Q("knx-project-view"),R="3.3.0";class T extends i.WF{disconnectedCallback(){super.disconnectedCallback(),this._subscribed&&(this._subscribed(),this._subscribed=void 0)}async firstUpdated(){(0,g.ke)(this.hass).then((e=>{this._lastTelegrams=e})).catch((e=>{O.error("getGroupTelegrams",e),(0,c.o)("/knx/error",{replace:!0,data:e})})),this._subscribed=await(0,g.EE)(this.hass,(e=>{this.telegram_callback(e)}))}_isGroupRangeAvailable(){var e,t;const a=null!==(e=null===(t=this.knx.projectData)||void 0===t?void 0:t.info.xknxproject_version)&&void 0!==e?e:"0.0.0";O.debug("project version: "+a),this._groupRangeAvailable=(0,u.U)(a,R,">=")}telegram_callback(e){this._lastTelegrams=Object.assign(Object.assign({},this._lastTelegrams),{},{[e.destination]:e})}_groupAddressMenu(e){var t;const a=[];return a.push({path:Z,label:this.knx.localize("project_view_menu_view_telegrams"),action:()=>{(0,c.o)(`/knx/group_monitor?destination=${e.address}`)}}),1===(null===(t=e.dpt)||void 0===t?void 0:t.main)&&a.push({path:C,label:this.knx.localize("project_view_menu_create_binary_sensor"),action:()=>{(0,c.o)("/knx/entities/create/binary_sensor?knx.ga_sensor.state="+e.address)}}),(0,i.qy)(m||(m=z`
      <ha-icon-overflow-menu .hass=${0} narrow .items=${0}> </ha-icon-overflow-menu>
    `),this.hass,a)}_getRows(e){return e.length?Object.entries(this.knx.projectData.group_addresses).reduce(((t,[a,r])=>(e.includes(a)&&t.push(r),t)),[]):Object.values(this.knx.projectData.group_addresses)}_visibleAddressesChanged(e){this._visibleGroupAddresses=e.detail.groupAddresses}render(){return this.hass?(0,i.qy)(f||(f=z` <hass-tabs-subpage
      .hass=${0}
      .narrow=${0}
      .route=${0}
      .tabs=${0}
      .localizeFunc=${0}
    >
      ${0}
    </hass-tabs-subpage>`),this.hass,this.narrow,this.route,this.tabs,this.knx.localize,this._projectLoadTask.render({initial:()=>(0,i.qy)(x||(x=z`
          <hass-loading-screen .message=${0}></hass-loading-screen>
        `),"Waiting to fetch project data."),pending:()=>(0,i.qy)(w||(w=z`
          <hass-loading-screen .message=${0}></hass-loading-screen>
        `),"Loading KNX project data."),error:e=>(O.error("Error loading KNX project",e),(0,i.qy)(k||(k=z`<ha-alert alert-type="error">"Error loading KNX project"</ha-alert>`))),complete:()=>this.renderMain()})):(0,i.qy)(_||(_=z` <hass-loading-screen></hass-loading-screen> `))}renderMain(){const e=this._getRows(this._visibleGroupAddresses);return this.knx.projectData?(0,i.qy)($||($=z`${0}
          <div class="sections">
            ${0}
            <ha-data-table
              class="ga-table"
              .hass=${0}
              .columns=${0}
              .data=${0}
              .hasFab=${0}
              .searchLabel=${0}
              .clickable=${0}
            ></ha-data-table>
          </div>`),this.narrow&&this._groupRangeAvailable?(0,i.qy)(M||(M=z`<ha-icon-button
                slot="toolbar-icon"
                .label=${0}
                .path=${0}
                @click=${0}
              ></ha-icon-button>`),this.hass.localize("ui.components.related-filter-menu.filter"),D,this._toggleRangeSelector):i.s6,this._groupRangeAvailable?(0,i.qy)(A||(A=z`
                  <knx-project-tree-view
                    .data=${0}
                    @knx-group-range-selection-changed=${0}
                  ></knx-project-tree-view>
                `),this.knx.projectData,this._visibleAddressesChanged):i.s6,this.hass,this._columns(this.narrow,this.hass.language),e,!1,this.hass.localize("ui.components.data-table.search"),!1):(0,i.qy)(H||(H=z` <ha-card .header=${0}>
          <div class="card-content">
            <p>${0}</p>
          </div>
        </ha-card>`),this.knx.localize("attention"),this.knx.localize("project_view_upload"))}_toggleRangeSelector(){this.rangeSelectorHidden=!this.rangeSelectorHidden}constructor(...e){super(...e),this.rangeSelectorHidden=!0,this._visibleGroupAddresses=[],this._groupRangeAvailable=!1,this._lastTelegrams={},this._projectLoadTask=new s.YZ(this,{args:()=>[],task:async()=>{this.knx.projectInfo&&!this.knx.projectData&&await this.knx.loadProject(),this._isGroupRangeAvailable()}}),this._columns=(0,l.A)(((e,t)=>({address:{filterable:!0,sortable:!0,title:this.knx.localize("project_view_table_address"),flex:1,minWidth:"100px"},name:{filterable:!0,sortable:!0,title:this.knx.localize("project_view_table_name"),flex:3},dpt:{sortable:!0,filterable:!0,title:this.knx.localize("project_view_table_dpt"),flex:1,minWidth:"82px",template:e=>e.dpt?(0,i.qy)(j||(j=z`<span style="display:inline-block;width:24px;text-align:right;"
                  >${0}</span
                >${0} `),e.dpt.main,e.dpt.sub?"."+e.dpt.sub.toString().padStart(3,"0"):""):""},lastValue:{filterable:!0,title:this.knx.localize("project_view_table_last_value"),flex:2,template:e=>{const t=this._lastTelegrams[e.address];if(!t)return"";const a=v.e4.payload(t);return null==t.value?(0,i.qy)(S||(S=z`<code>${0}</code>`),a):(0,i.qy)(V||(V=z`<div title=${0}>
            ${0}
          </div>`),a,v.e4.valueWithUnit(this._lastTelegrams[e.address]))}},updated:{title:this.knx.localize("project_view_table_updated"),flex:1,showNarrow:!1,template:e=>{const t=this._lastTelegrams[e.address];if(!t)return"";const a=`${v.e4.dateWithMilliseconds(t)}\n\n${t.source} ${t.source_name}`;return(0,i.qy)(L||(L=z`<div title=${0}>
            ${0}
          </div>`),a,(0,p.K)(new Date(t.timestamp),this.hass.locale))}},actions:{title:"",minWidth:"72px",type:"overflow-menu",template:e=>this._groupAddressMenu(e)}})))}}T.styles=(0,i.AH)(q||(q=z`
    hass-loading-screen {
      --app-header-background-color: var(--sidebar-background-color);
      --app-header-text-color: var(--sidebar-text-color);
    }
    .sections {
      display: flex;
      flex-direction: row;
      height: 100%;
    }

    :host([narrow]) knx-project-tree-view {
      position: absolute;
      max-width: calc(100% - 60px); /* 100% -> max 871px before not narrow */
      z-index: 1;
      right: 0;
      transition: 0.5s;
      border-left: 1px solid var(--divider-color);
    }

    :host([narrow][range-selector-hidden]) knx-project-tree-view {
      width: 0;
    }

    :host(:not([narrow])) knx-project-tree-view {
      max-width: 255px; /* min 616px - 816px for tree-view + ga-table (depending on side menu) */
    }

    .ga-table {
      flex: 1;
    }
  `)),(0,o.__decorate)([(0,n.MZ)({type:Object})],T.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],T.prototype,"knx",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],T.prototype,"narrow",void 0),(0,o.__decorate)([(0,n.MZ)({type:Object})],T.prototype,"route",void 0),(0,o.__decorate)([(0,n.MZ)({type:Array,reflect:!1})],T.prototype,"tabs",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0,attribute:"range-selector-hidden"})],T.prototype,"rangeSelectorHidden",void 0),(0,o.__decorate)([(0,n.wk)()],T.prototype,"_visibleGroupAddresses",void 0),(0,o.__decorate)([(0,n.wk)()],T.prototype,"_groupRangeAvailable",void 0),(0,o.__decorate)([(0,n.wk)()],T.prototype,"_subscribed",void 0),(0,o.__decorate)([(0,n.wk)()],T.prototype,"_lastTelegrams",void 0),T=(0,o.__decorate)([(0,n.EM)("knx-project-view")],T),r()}catch(m){r(m)}}))}}]);
//# sourceMappingURL=5722.8a1d91ebf7be25f3.js.map