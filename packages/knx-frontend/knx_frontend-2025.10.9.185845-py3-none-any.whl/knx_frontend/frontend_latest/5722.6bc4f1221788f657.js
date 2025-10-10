export const __webpack_id__="5722";export const __webpack_ids__=["5722"];export const __webpack_modules__={895:function(e,t,a){a.d(t,{PE:()=>n});var r=a(6423),o=a(95226);const i=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"],n=e=>e.first_weekday===o.zt.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(e.language).weekInfo.firstDay%7:(0,r.S)(e.language)%7:i.includes(e.first_weekday)?i.indexOf(e.first_weekday):1},45980:function(e,t,a){a.a(e,(async function(e,r){try{a.d(t,{K:()=>d});var o=a(96904),i=a(65940),n=a(83516),s=e([o,n]);[o,n]=s.then?(await s)():s;const l=(0,i.A)((e=>new Intl.RelativeTimeFormat(e.language,{numeric:"auto"}))),d=(e,t,a,r=!0)=>{const o=(0,n.x)(e,a,t);return r?l(t).format(o.value,o.unit):Intl.NumberFormat(t.language,{style:"unit",unit:o.unit,unitDisplay:"long"}).format(Math.abs(o.value))};r()}catch(l){r(l)}}))},83516:function(e,t,a){a.a(e,(async function(e,r){try{a.d(t,{x:()=>h});var o=a(41484),i=a(88258),n=a(39826),s=a(895);const d=1e3,c=60,p=60*c;function h(e,t=Date.now(),a,r={}){const l={...u,...r||{}},h=(+e-+t)/d;if(Math.abs(h)<l.second)return{value:Math.round(h),unit:"second"};const g=h/c;if(Math.abs(g)<l.minute)return{value:Math.round(g),unit:"minute"};const b=h/p;if(Math.abs(b)<l.hour)return{value:Math.round(b),unit:"hour"};const v=new Date(e),m=new Date(t);v.setHours(0,0,0,0),m.setHours(0,0,0,0);const _=(0,o.c)(v,m);if(0===_)return{value:Math.round(b),unit:"hour"};if(Math.abs(_)<l.day)return{value:_,unit:"day"};const y=(0,s.PE)(a),f=(0,i.k)(v,{weekStartsOn:y}),x=(0,i.k)(m,{weekStartsOn:y}),w=(0,n.I)(f,x);if(0===w)return{value:_,unit:"day"};if(Math.abs(w)<l.week)return{value:w,unit:"week"};const k=v.getFullYear()-m.getFullYear(),$=12*k+v.getMonth()-m.getMonth();return 0===$?{value:w,unit:"week"}:Math.abs($)<l.month||0===k?{value:$,unit:"month"}:{value:Math.round(k),unit:"year"}}const u={second:45,minute:45,hour:22,day:5,week:4,month:11};r()}catch(l){r(l)}}))},23749:function(e,t,a){a.r(t);var r=a(69868),o=a(84922),i=a(11991),n=a(75907),s=a(73120);a(93672),a(95635);const l={info:"M11,9H13V7H11M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,17H13V11H11V17Z",warning:"M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16",error:"M11,15H13V17H11V15M11,7H13V13H11V7M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20Z",success:"M20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4C12.76,4 13.5,4.11 14.2,4.31L15.77,2.74C14.61,2.26 13.34,2 12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12M7.91,10.08L6.5,11.5L11,16L21,6L19.59,4.58L11,13.17L7.91,10.08Z"};class d extends o.WF{render(){return o.qy`
      <div
        class="issue-type ${(0,n.H)({[this.alertType]:!0})}"
        role="alert"
      >
        <div class="icon ${this.title?"":"no-title"}">
          <slot name="icon">
            <ha-svg-icon .path=${l[this.alertType]}></ha-svg-icon>
          </slot>
        </div>
        <div class=${(0,n.H)({content:!0,narrow:this.narrow})}>
          <div class="main-content">
            ${this.title?o.qy`<div class="title">${this.title}</div>`:o.s6}
            <slot></slot>
          </div>
          <div class="action">
            <slot name="action">
              ${this.dismissable?o.qy`<ha-icon-button
                    @click=${this._dismissClicked}
                    label="Dismiss alert"
                    .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
                  ></ha-icon-button>`:o.s6}
            </slot>
          </div>
        </div>
      </div>
    `}_dismissClicked(){(0,s.r)(this,"alert-dismissed-clicked")}constructor(...e){super(...e),this.title="",this.alertType="info",this.dismissable=!1,this.narrow=!1}}d.styles=o.AH`
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
  `,(0,r.__decorate)([(0,i.MZ)()],d.prototype,"title",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:"alert-type"})],d.prototype,"alertType",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean})],d.prototype,"dismissable",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean})],d.prototype,"narrow",void 0),d=(0,r.__decorate)([(0,i.EM)("ha-alert")],d)},86853:function(e,t,a){var r=a(69868),o=a(84922),i=a(11991);class n extends o.WF{render(){return o.qy`
      ${this.header?o.qy`<h1 class="card-header">${this.header}</h1>`:o.s6}
      <slot></slot>
    `}constructor(...e){super(...e),this.raised=!1}}n.styles=o.AH`
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
  `,(0,r.__decorate)([(0,i.MZ)()],n.prototype,"header",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean,reflect:!0})],n.prototype,"raised",void 0),n=(0,r.__decorate)([(0,i.EM)("ha-card")],n)},35881:function(e,t,a){a.a(e,(async function(e,r){try{a.r(t),a.d(t,{HaIconOverflowMenu:()=>h});var o=a(69868),i=a(84922),n=a(11991),s=a(75907),l=a(83566),d=(a(61647),a(93672),a(95635),a(89652)),c=(a(70154),a(90666),e([d]));d=(c.then?(await c)():c)[0];const p="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z";class h extends i.WF{render(){return i.qy`
      ${this.narrow?i.qy` <!-- Collapsed representation for small screens -->
            <ha-md-button-menu
              @click=${this._handleIconOverflowMenuOpened}
              positioning="popover"
            >
              <ha-icon-button
                .label=${this.hass.localize("ui.common.overflow_menu")}
                .path=${p}
                slot="trigger"
              ></ha-icon-button>

              ${this.items.map((e=>e.divider?i.qy`<ha-md-divider
                      role="separator"
                      tabindex="-1"
                    ></ha-md-divider>`:i.qy`<ha-md-menu-item
                      ?disabled=${e.disabled}
                      .clickAction=${e.action}
                      class=${(0,s.H)({warning:Boolean(e.warning)})}
                    >
                      <ha-svg-icon
                        slot="start"
                        class=${(0,s.H)({warning:Boolean(e.warning)})}
                        .path=${e.path}
                      ></ha-svg-icon>
                      ${e.label}
                    </ha-md-menu-item> `))}
            </ha-md-button-menu>`:i.qy`
            <!-- Icon representation for big screens -->
            ${this.items.map((e=>e.narrowOnly?i.s6:e.divider?i.qy`<div role="separator"></div>`:i.qy`<ha-tooltip
                        .disabled=${!e.tooltip}
                        .for="icon-button-${e.label}"
                        >${e.tooltip??""} </ha-tooltip
                      ><ha-icon-button
                        .id="icon-button-${e.label}"
                        @click=${e.action}
                        .label=${e.label}
                        .path=${e.path}
                        ?disabled=${e.disabled}
                      ></ha-icon-button> `))}
          `}
    `}_handleIconOverflowMenuOpened(e){e.stopPropagation()}static get styles(){return[l.RF,i.AH`
        :host {
          display: flex;
          justify-content: flex-end;
        }
        div[role="separator"] {
          border-right: 1px solid var(--divider-color);
          width: 1px;
        }
      `]}constructor(...e){super(...e),this.items=[],this.narrow=!1}}(0,o.__decorate)([(0,n.MZ)({attribute:!1})],h.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)({type:Array})],h.prototype,"items",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],h.prototype,"narrow",void 0),h=(0,o.__decorate)([(0,n.EM)("ha-icon-overflow-menu")],h),r()}catch(p){r(p)}}))},89652:function(e,t,a){a.a(e,(async function(e,t){try{var r=a(69868),o=a(28784),i=a(84922),n=a(11991),s=e([o]);o=(s.then?(await s)():s)[0];class l extends o.A{static get styles(){return[o.A.styles,i.AH`
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
      `]}constructor(...e){super(...e),this.showDelay=150,this.hideDelay=400}}(0,r.__decorate)([(0,n.MZ)({attribute:"show-delay",type:Number})],l.prototype,"showDelay",void 0),(0,r.__decorate)([(0,n.MZ)({attribute:"hide-delay",type:Number})],l.prototype,"hideDelay",void 0),l=(0,r.__decorate)([(0,n.EM)("ha-tooltip")],l),t()}catch(l){t(l)}}))},99478:function(e,t,a){var r=a(69868),o=a(84922),i=a(11991),n=a(75907),s=a(73120);const l=new(a(92095).Q)("knx-project-tree-view");class d extends o.WF{connectedCallback(){super.connectedCallback();const e=t=>{Object.entries(t).forEach((([t,a])=>{a.group_addresses.length>0&&(this._selectableRanges[t]={selected:!1,groupAddresses:a.group_addresses}),e(a.group_ranges)}))};e(this.data.group_ranges),l.debug("ranges",this._selectableRanges)}render(){return o.qy`<div class="ha-tree-view">${this._recurseData(this.data.group_ranges)}</div>`}_recurseData(e,t=0){const a=Object.entries(e).map((([e,a])=>{const r=Object.keys(a.group_ranges).length>0;if(!(r||a.group_addresses.length>0))return o.s6;const i=e in this._selectableRanges,s=!!i&&this._selectableRanges[e].selected,l={"range-item":!0,"root-range":0===t,"sub-range":t>0,selectable:i,"selected-range":s,"non-selected-range":i&&!s},d=o.qy`<div
        class=${(0,n.H)(l)}
        toggle-range=${i?e:o.s6}
        @click=${i?this.multiselect?this._selectionChangedMulti:this._selectionChangedSingle:o.s6}
      >
        <span class="range-key">${e}</span>
        <span class="range-text">${a.name}</span>
      </div>`;if(r){const e={"root-group":0===t,"sub-group":0!==t};return o.qy`<div class=${(0,n.H)(e)}>
          ${d} ${this._recurseData(a.group_ranges,t+1)}
        </div>`}return o.qy`${d}`}));return o.qy`${a}`}_selectionChangedMulti(e){const t=e.target.getAttribute("toggle-range");this._selectableRanges[t].selected=!this._selectableRanges[t].selected,this._selectionUpdate(),this.requestUpdate()}_selectionChangedSingle(e){const t=e.target.getAttribute("toggle-range"),a=this._selectableRanges[t].selected;Object.values(this._selectableRanges).forEach((e=>{e.selected=!1})),this._selectableRanges[t].selected=!a,this._selectionUpdate(),this.requestUpdate()}_selectionUpdate(){const e=Object.values(this._selectableRanges).reduce(((e,t)=>t.selected?e.concat(t.groupAddresses):e),[]);l.debug("selection changed",e),(0,s.r)(this,"knx-group-range-selection-changed",{groupAddresses:e})}constructor(...e){super(...e),this.multiselect=!1,this._selectableRanges={}}}d.styles=o.AH`
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
  `,(0,r.__decorate)([(0,i.MZ)({attribute:!1})],d.prototype,"data",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:!1})],d.prototype,"multiselect",void 0),(0,r.__decorate)([(0,i.wk)()],d.prototype,"_selectableRanges",void 0),d=(0,r.__decorate)([(0,i.EM)("knx-project-tree-view")],d)},93060:function(e,t,a){a.d(t,{CY:()=>l,HF:()=>s,RL:()=>v,Vt:()=>i,Zc:()=>n,e4:()=>o,u_:()=>b});var r=a(90227);const o={payload:e=>null==e.payload?"":Array.isArray(e.payload)?e.payload.reduce(((e,t)=>e+t.toString(16).padStart(2,"0")),"0x"):e.payload.toString(),valueWithUnit:e=>null==e.value?"":"number"==typeof e.value||"boolean"==typeof e.value||"string"==typeof e.value?e.value.toString()+(e.unit?" "+e.unit:""):(0,r.Bh)(e.value),timeWithMilliseconds:e=>new Date(e.timestamp).toLocaleTimeString(["en-US"],{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),dateWithMilliseconds:e=>new Date(e.timestamp).toLocaleTimeString([],{year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),dptNumber:e=>null==e.dpt_main?"":null==e.dpt_sub?e.dpt_main.toString():e.dpt_main.toString()+"."+e.dpt_sub.toString().padStart(3,"0"),dptNameNumber:e=>{const t=o.dptNumber(e);return null==e.dpt_name?`DPT ${t}`:t?`DPT ${t} ${e.dpt_name}`:e.dpt_name}},i=e=>null==e?"":e.main+(e.sub?"."+e.sub.toString().padStart(3,"0"):""),n=e=>e.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),s=e=>e.toLocaleDateString(void 0,{year:"numeric",month:"2-digit",day:"2-digit"})+", "+e.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),l=e=>{const t=new Date(e),a=e.match(/\.(\d{6})/),r=a?a[1]:"000000";return t.toLocaleDateString(void 0,{year:"numeric",month:"2-digit",day:"2-digit"})+", "+t.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit"})+"."+r},d=1e3,c=1e3,p=60*c,h=60*p,u=2,g=3;function b(e){const t=e.indexOf(".");if(-1===t)return 1e3*Date.parse(e);let a=e.indexOf("Z",t);-1===a&&(a=e.indexOf("+",t),-1===a&&(a=e.indexOf("-",t))),-1===a&&(a=e.length);const r=e.slice(0,t)+e.slice(a),o=Date.parse(r);let i=e.slice(t+1,a);return i.length<6?i=i.padEnd(6,"0"):i.length>6&&(i=i.slice(0,6)),1e3*o+Number(i)}function v(e,t="milliseconds"){if(null==e)return"—";const a=e<0?"-":"",r=Math.abs(e),o="milliseconds"===t?Math.round(r/d):Math.floor(r/d),i="microseconds"===t?r%d:0,n=Math.floor(o/h),s=Math.floor(o%h/p),l=Math.floor(o%p/c),b=o%c,v=e=>e.toString().padStart(u,"0"),m=e=>e.toString().padStart(g,"0"),_="microseconds"===t?`.${m(b)}${m(i)}`:`.${m(b)}`,y=`${v(s)}:${v(l)}`;return`${a}${n>0?`${v(n)}:${y}`:y}${_}`}},65857:function(e,t,a){a.a(e,(async function(e,r){try{a.r(t),a.d(t,{KNXProjectView:()=>k});var o=a(69868),i=a(84922),n=a(11991),s=a(68476),l=a(65940),d=a(68985),c=a(92491),p=(a(54885),a(23749),a(86853),a(93672),a(35881)),h=(a(21339),a(45980)),u=(a(99478),a(22288)),g=a(49432),b=a(92095),v=a(93060),m=e([c,p,h]);[c,p,h]=m.then?(await m)():m;const _="M6,13H18V11H6M3,6V8H21V6M10,18H14V16H10V18Z",y="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",f="M18 7C16.9 7 16 7.9 16 9V15C16 16.1 16.9 17 18 17H20C21.1 17 22 16.1 22 15V11H20V15H18V9H22V7H18M2 7V17H8V15H4V7H2M11 7C9.9 7 9 7.9 9 9V15C9 16.1 9.9 17 11 17H13C14.1 17 15 16.1 15 15V9C15 7.9 14.1 7 13 7H11M11 9H13V15H11V9Z",x=new b.Q("knx-project-view"),w="3.3.0";class k extends i.WF{disconnectedCallback(){super.disconnectedCallback(),this._subscribed&&(this._subscribed(),this._subscribed=void 0)}async firstUpdated(){(0,g.ke)(this.hass).then((e=>{this._lastTelegrams=e})).catch((e=>{x.error("getGroupTelegrams",e),(0,d.o)("/knx/error",{replace:!0,data:e})})),this._subscribed=await(0,g.EE)(this.hass,(e=>{this.telegram_callback(e)}))}_isGroupRangeAvailable(){const e=this.knx.projectData?.info.xknxproject_version??"0.0.0";x.debug("project version: "+e),this._groupRangeAvailable=(0,u.U)(e,w,">=")}telegram_callback(e){this._lastTelegrams={...this._lastTelegrams,[e.destination]:e}}_groupAddressMenu(e){const t=[];return t.push({path:f,label:this.knx.localize("project_view_menu_view_telegrams"),action:()=>{(0,d.o)(`/knx/group_monitor?destination=${e.address}`)}}),1===e.dpt?.main&&t.push({path:y,label:this.knx.localize("project_view_menu_create_binary_sensor"),action:()=>{(0,d.o)("/knx/entities/create/binary_sensor?knx.ga_sensor.state="+e.address)}}),i.qy`
      <ha-icon-overflow-menu .hass=${this.hass} narrow .items=${t}> </ha-icon-overflow-menu>
    `}_getRows(e){return e.length?Object.entries(this.knx.projectData.group_addresses).reduce(((t,[a,r])=>(e.includes(a)&&t.push(r),t)),[]):Object.values(this.knx.projectData.group_addresses)}_visibleAddressesChanged(e){this._visibleGroupAddresses=e.detail.groupAddresses}render(){return this.hass?i.qy` <hass-tabs-subpage
      .hass=${this.hass}
      .narrow=${this.narrow}
      .route=${this.route}
      .tabs=${this.tabs}
      .localizeFunc=${this.knx.localize}
    >
      ${this._projectLoadTask.render({initial:()=>i.qy`
          <hass-loading-screen .message=${"Waiting to fetch project data."}></hass-loading-screen>
        `,pending:()=>i.qy`
          <hass-loading-screen .message=${"Loading KNX project data."}></hass-loading-screen>
        `,error:e=>(x.error("Error loading KNX project",e),i.qy`<ha-alert alert-type="error">"Error loading KNX project"</ha-alert>`),complete:()=>this.renderMain()})}
    </hass-tabs-subpage>`:i.qy` <hass-loading-screen></hass-loading-screen> `}renderMain(){const e=this._getRows(this._visibleGroupAddresses);return this.knx.projectData?i.qy`${this.narrow&&this._groupRangeAvailable?i.qy`<ha-icon-button
                slot="toolbar-icon"
                .label=${this.hass.localize("ui.components.related-filter-menu.filter")}
                .path=${_}
                @click=${this._toggleRangeSelector}
              ></ha-icon-button>`:i.s6}
          <div class="sections">
            ${this._groupRangeAvailable?i.qy`
                  <knx-project-tree-view
                    .data=${this.knx.projectData}
                    @knx-group-range-selection-changed=${this._visibleAddressesChanged}
                  ></knx-project-tree-view>
                `:i.s6}
            <ha-data-table
              class="ga-table"
              .hass=${this.hass}
              .columns=${this._columns(this.narrow,this.hass.language)}
              .data=${e}
              .hasFab=${!1}
              .searchLabel=${this.hass.localize("ui.components.data-table.search")}
              .clickable=${!1}
            ></ha-data-table>
          </div>`:i.qy` <ha-card .header=${this.knx.localize("attention")}>
          <div class="card-content">
            <p>${this.knx.localize("project_view_upload")}</p>
          </div>
        </ha-card>`}_toggleRangeSelector(){this.rangeSelectorHidden=!this.rangeSelectorHidden}constructor(...e){super(...e),this.rangeSelectorHidden=!0,this._visibleGroupAddresses=[],this._groupRangeAvailable=!1,this._lastTelegrams={},this._projectLoadTask=new s.YZ(this,{args:()=>[],task:async()=>{this.knx.projectInfo&&!this.knx.projectData&&await this.knx.loadProject(),this._isGroupRangeAvailable()}}),this._columns=(0,l.A)(((e,t)=>({address:{filterable:!0,sortable:!0,title:this.knx.localize("project_view_table_address"),flex:1,minWidth:"100px"},name:{filterable:!0,sortable:!0,title:this.knx.localize("project_view_table_name"),flex:3},dpt:{sortable:!0,filterable:!0,title:this.knx.localize("project_view_table_dpt"),flex:1,minWidth:"82px",template:e=>e.dpt?i.qy`<span style="display:inline-block;width:24px;text-align:right;"
                  >${e.dpt.main}</span
                >${e.dpt.sub?"."+e.dpt.sub.toString().padStart(3,"0"):""} `:""},lastValue:{filterable:!0,title:this.knx.localize("project_view_table_last_value"),flex:2,template:e=>{const t=this._lastTelegrams[e.address];if(!t)return"";const a=v.e4.payload(t);return null==t.value?i.qy`<code>${a}</code>`:i.qy`<div title=${a}>
            ${v.e4.valueWithUnit(this._lastTelegrams[e.address])}
          </div>`}},updated:{title:this.knx.localize("project_view_table_updated"),flex:1,showNarrow:!1,template:e=>{const t=this._lastTelegrams[e.address];if(!t)return"";const a=`${v.e4.dateWithMilliseconds(t)}\n\n${t.source} ${t.source_name}`;return i.qy`<div title=${a}>
            ${(0,h.K)(new Date(t.timestamp),this.hass.locale)}
          </div>`}},actions:{title:"",minWidth:"72px",type:"overflow-menu",template:e=>this._groupAddressMenu(e)}})))}}k.styles=i.AH`
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
  `,(0,o.__decorate)([(0,n.MZ)({type:Object})],k.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],k.prototype,"knx",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],k.prototype,"narrow",void 0),(0,o.__decorate)([(0,n.MZ)({type:Object})],k.prototype,"route",void 0),(0,o.__decorate)([(0,n.MZ)({type:Array,reflect:!1})],k.prototype,"tabs",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0,attribute:"range-selector-hidden"})],k.prototype,"rangeSelectorHidden",void 0),(0,o.__decorate)([(0,n.wk)()],k.prototype,"_visibleGroupAddresses",void 0),(0,o.__decorate)([(0,n.wk)()],k.prototype,"_groupRangeAvailable",void 0),(0,o.__decorate)([(0,n.wk)()],k.prototype,"_subscribed",void 0),(0,o.__decorate)([(0,n.wk)()],k.prototype,"_lastTelegrams",void 0),k=(0,o.__decorate)([(0,n.EM)("knx-project-view")],k),r()}catch(_){r(_)}}))}};
//# sourceMappingURL=5722.6bc4f1221788f657.js.map