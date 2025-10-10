/*! For license information please see 50.7c7bc2c8bca8a2e2.js.LICENSE.txt */
"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["50"],{895:function(e,t,i){i.a(e,(async function(e,o){try{i.d(t,{PE:function(){return d}});i(79827);var r=i(96904),s=i(6423),n=i(95075),a=e([r]);r=(a.then?(await a)():a)[0];const l=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"],d=e=>e.first_weekday===n.zt.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(e.language).weekInfo.firstDay%7:(0,s.S)(e.language)%7:l.includes(e.first_weekday)?l.indexOf(e.first_weekday):1;o()}catch(l){o(l)}}))},45980:function(e,t,i){i.a(e,(async function(e,o){try{i.d(t,{K:function(){return d}});var r=i(96904),s=i(65940),n=i(83516),a=e([r,n]);[r,n]=a.then?(await a)():a;const l=(0,s.A)((e=>new Intl.RelativeTimeFormat(e.language,{numeric:"auto"}))),d=(e,t,i,o=!0)=>{const r=(0,n.x)(e,i,t);return o?l(t).format(r.value,r.unit):Intl.NumberFormat(t.language,{style:"unit",unit:r.unit,unitDisplay:"long"}).format(Math.abs(r.value))};o()}catch(l){o(l)}}))},8692:function(e,t,i){i.d(t,{Z:function(){return o}});const o=e=>e.charAt(0).toUpperCase()+e.slice(1)},85735:function(e,t,i){i.d(t,{Y:function(){return o}});i(42124),i(86581),i(67579),i(47849),i(30500);const o=(e,t="_")=>{const i="àáâäæãåāăąабçćčđďдèéêëēėęěеёэфğǵгḧхîïíīįìıİийкłлḿмñńǹňнôöòóœøōõőоṕпŕřрßśšşșсťțтûüùúūǘůűųувẃẍÿýыžźżз·",o=`aaaaaaaaaaabcccdddeeeeeeeeeeefggghhiiiiiiiiijkllmmnnnnnoooooooooopprrrsssssstttuuuuuuuuuuvwxyyyzzzz${t}`,r=new RegExp(i.split("").join("|"),"g"),s={"ж":"zh","х":"kh","ц":"ts","ч":"ch","ш":"sh","щ":"shch","ю":"iu","я":"ia"};let n;return""===e?n="":(n=e.toString().toLowerCase().replace(r,(e=>o.charAt(i.indexOf(e)))).replace(/[а-я]/g,(e=>s[e]||"")).replace(/(\d),(?=\d)/g,"$1").replace(/[^a-z0-9]+/g,t).replace(new RegExp(`(${t})\\1+`,"g"),"$1").replace(new RegExp(`^${t}+`),"").replace(new RegExp(`${t}+$`),""),""===n&&(n="unknown")),n}},83516:function(e,t,i){i.a(e,(async function(e,o){try{i.d(t,{x:function(){return u}});i(12977);var r=i(41484),s=i(88258),n=i(39826),a=i(895),l=e([a]);a=(l.then?(await l)():l)[0];const c=1e3,h=60,p=60*h;function u(e,t=Date.now(),i,o={}){const l=Object.assign(Object.assign({},g),o||{}),d=(+e-+t)/c;if(Math.abs(d)<l.second)return{value:Math.round(d),unit:"second"};const u=d/h;if(Math.abs(u)<l.minute)return{value:Math.round(u),unit:"minute"};const m=d/p;if(Math.abs(m)<l.hour)return{value:Math.round(m),unit:"hour"};const _=new Date(e),f=new Date(t);_.setHours(0,0,0,0),f.setHours(0,0,0,0);const b=(0,r.c)(_,f);if(0===b)return{value:Math.round(m),unit:"hour"};if(Math.abs(b)<l.day)return{value:b,unit:"day"};const x=(0,a.PE)(i),v=(0,s.k)(_,{weekStartsOn:x}),y=(0,s.k)(f,{weekStartsOn:x}),k=(0,n.I)(v,y);if(0===k)return{value:b,unit:"day"};if(Math.abs(k)<l.week)return{value:k,unit:"week"};const $=_.getFullYear()-f.getFullYear(),w=12*$+_.getMonth()-f.getMonth();return 0===w?{value:k,unit:"week"}:Math.abs(w)<l.month||0===$?{value:w,unit:"month"}:{value:Math.round($),unit:"year"}}const g={second:45,minute:45,hour:22,day:5,week:4,month:11};o()}catch(d){o(d)}}))},72847:function(e,t,i){i.d(t,{l:function(){return u}});i(35748),i(95013),i(37216);var o=i(69868),r=i(66630),s=i(34119),n=i(84922),a=i(11991);i(9974),i(93672);let l,d,c,h=e=>e;const p=["button","ha-list-item"],u=(e,t)=>{var i;return(0,n.qy)(l||(l=h`
  <div class="header_title">
    <ha-icon-button
      .label=${0}
      .path=${0}
      dialogAction="close"
      class="header_button"
    ></ha-icon-button>
    <span>${0}</span>
  </div>
`),null!==(i=null==e?void 0:e.localize("ui.common.close"))&&void 0!==i?i:"Close","M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",t)};class g extends r.u{scrollToPos(e,t){var i;null===(i=this.contentElement)||void 0===i||i.scrollTo(e,t)}renderHeading(){return(0,n.qy)(d||(d=h`<slot name="heading"> ${0} </slot>`),super.renderHeading())}firstUpdated(){var e;super.firstUpdated(),this.suppressDefaultPressSelector=[this.suppressDefaultPressSelector,p].join(", "),this._updateScrolledAttribute(),null===(e=this.contentElement)||void 0===e||e.addEventListener("scroll",this._onScroll,{passive:!0})}disconnectedCallback(){super.disconnectedCallback(),this.contentElement.removeEventListener("scroll",this._onScroll)}_updateScrolledAttribute(){this.contentElement&&this.toggleAttribute("scrolled",0!==this.contentElement.scrollTop)}constructor(...e){super(...e),this._onScroll=()=>{this._updateScrolledAttribute()}}}g.styles=[s.R,(0,n.AH)(c||(c=h`
      :host([scrolled]) ::slotted(ha-dialog-header) {
        border-bottom: 1px solid
          var(--mdc-dialog-scroll-divider-color, rgba(0, 0, 0, 0.12));
      }
      .mdc-dialog {
        --mdc-dialog-scroll-divider-color: var(
          --dialog-scroll-divider-color,
          var(--divider-color)
        );
        z-index: var(--dialog-z-index, 8);
        -webkit-backdrop-filter: var(
          --ha-dialog-scrim-backdrop-filter,
          var(--dialog-backdrop-filter, none)
        );
        backdrop-filter: var(
          --ha-dialog-scrim-backdrop-filter,
          var(--dialog-backdrop-filter, none)
        );
        --mdc-dialog-box-shadow: var(--dialog-box-shadow, none);
        --mdc-typography-headline6-font-weight: var(--ha-font-weight-normal);
        --mdc-typography-headline6-font-size: 1.574rem;
      }
      .mdc-dialog__actions {
        justify-content: var(--justify-action-buttons, flex-end);
        padding: 12px 16px 16px 16px;
      }
      .mdc-dialog__actions span:nth-child(1) {
        flex: var(--secondary-action-button-flex, unset);
      }
      .mdc-dialog__actions span:nth-child(2) {
        flex: var(--primary-action-button-flex, unset);
      }
      .mdc-dialog__container {
        align-items: var(--vertical-align-dialog, center);
      }
      .mdc-dialog__title {
        padding: 16px 16px 0 16px;
      }
      .mdc-dialog__title:has(span) {
        padding: 12px 12px 0;
      }
      .mdc-dialog__title::before {
        content: unset;
      }
      .mdc-dialog .mdc-dialog__content {
        position: var(--dialog-content-position, relative);
        padding: var(--dialog-content-padding, 24px);
      }
      :host([hideactions]) .mdc-dialog .mdc-dialog__content {
        padding-bottom: var(--dialog-content-padding, 24px);
      }
      .mdc-dialog .mdc-dialog__surface {
        position: var(--dialog-surface-position, relative);
        top: var(--dialog-surface-top);
        margin-top: var(--dialog-surface-margin-top);
        min-width: var(--mdc-dialog-min-width, 100vw);
        min-height: var(--mdc-dialog-min-height, auto);
        border-radius: var(--ha-dialog-border-radius, 24px);
        -webkit-backdrop-filter: var(--ha-dialog-surface-backdrop-filter, none);
        backdrop-filter: var(--ha-dialog-surface-backdrop-filter, none);
        background: var(
          --ha-dialog-surface-background,
          var(--mdc-theme-surface, #fff)
        );
      }
      :host([flexContent]) .mdc-dialog .mdc-dialog__content {
        display: flex;
        flex-direction: column;
      }

      @media all and (max-width: 450px), all and (max-height: 500px) {
        .mdc-dialog .mdc-dialog__surface {
          min-height: 100vh;
          max-height: 100vh;
          padding-top: var(--safe-area-inset-top);
          padding-bottom: var(--safe-area-inset-bottom);
          padding-left: var(--safe-area-inset-left);
          padding-right: var(--safe-area-inset-right);
        }
      }

      .header_title {
        display: flex;
        align-items: center;
        direction: var(--direction);
      }
      .header_title span {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        display: block;
        padding-left: 4px;
        padding-right: 4px;
        margin-right: 12px;
        margin-inline-end: 12px;
        margin-inline-start: initial;
      }
      .header_button {
        text-decoration: none;
        color: inherit;
        inset-inline-start: initial;
        inset-inline-end: -12px;
        direction: var(--direction);
      }
      .dialog-actions {
        inset-inline-start: initial !important;
        inset-inline-end: 0px !important;
        direction: var(--direction);
      }
    `))],g=(0,o.__decorate)([(0,a.EM)("ha-dialog")],g)},51892:function(e,t,i){i.r(t),i.d(t,{HaIconButtonToggle:function(){return l}});i(35748),i(95013);var o=i(69868),r=i(84922),s=i(11991),n=i(93672);let a;class l extends n.HaIconButton{constructor(...e){super(...e),this.selected=!1}}l.styles=(0,r.AH)(a||(a=(e=>e)`
    :host {
      position: relative;
    }
    mwc-icon-button {
      position: relative;
      transition: color 180ms ease-in-out;
    }
    mwc-icon-button::before {
      opacity: 0;
      transition: opacity 180ms ease-in-out;
      background-color: var(--primary-text-color);
      border-radius: 20px;
      height: 40px;
      width: 40px;
      content: "";
      position: absolute;
      top: -10px;
      left: -10px;
      bottom: -10px;
      right: -10px;
      margin: auto;
      box-sizing: border-box;
    }
    :host([border-only]) mwc-icon-button::before {
      background-color: transparent;
      border: 2px solid var(--primary-text-color);
    }
    :host([selected]) mwc-icon-button {
      color: var(--primary-background-color);
    }
    :host([selected]:not([disabled])) mwc-icon-button::before {
      opacity: 1;
    }
  `)),(0,o.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0})],l.prototype,"selected",void 0),l=(0,o.__decorate)([(0,s.EM)("ha-icon-button-toggle")],l)},21873:function(e,t,i){i.a(e,(async function(e,t){try{i(35748),i(95013);var o=i(69868),r=i(22103),s=i(84922),n=i(11991),a=i(45980),l=i(8692),d=e([a]);a=(d.then?(await d)():d)[0];class c extends s.mN{disconnectedCallback(){super.disconnectedCallback(),this._clearInterval()}connectedCallback(){super.connectedCallback(),this.datetime&&this._startInterval()}createRenderRoot(){return this}firstUpdated(e){super.firstUpdated(e),this._updateRelative()}update(e){super.update(e),this._updateRelative()}_clearInterval(){this._interval&&(window.clearInterval(this._interval),this._interval=void 0)}_startInterval(){this._clearInterval(),this._interval=window.setInterval((()=>this._updateRelative()),6e4)}_updateRelative(){if(this.datetime){const e="string"==typeof this.datetime?(0,r.H)(this.datetime):this.datetime,t=(0,a.K)(e,this.hass.locale);this.innerHTML=this.capitalize?(0,l.Z)(t):t}else this.innerHTML=this.hass.localize("ui.components.relative_time.never")}constructor(...e){super(...e),this.capitalize=!1}}(0,o.__decorate)([(0,n.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],c.prototype,"datetime",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],c.prototype,"capitalize",void 0),c=(0,o.__decorate)([(0,n.EM)("ha-relative-time")],c),t()}catch(c){t(c)}}))},28210:function(e,t,i){i.d(t,{M:function(){return o}});i(67579),i(41190);const o=/(?:iphone|android|ipad)/i.test(navigator.userAgent)},17229:function(e,t,i){i.d(t,{C:function(){return o}});const o="ontouchstart"in window||navigator.maxTouchPoints>0||navigator.msMaxTouchPoints>0},8725:function(e,t,i){i(35748),i(95013);var o=i(69868),r=i(84922),s=i(11991),n=(i(93672),i(62754));let a,l,d,c=e=>e;class h extends n._{render(){return(0,r.qy)(a||(a=c`
      <div class="container">
        <div class="content-wrapper">
          <slot name="primary"></slot>
          <slot name="secondary"></slot>
        </div>
        <!-- Filter Button - conditionally rendered based on filterValue and filterDisabled -->
        ${0}
      </div>
    `),this.filterValue&&!this.filterDisabled?(0,r.qy)(l||(l=c`
              <div class="filter-button ${0}">
                <ha-icon-button
                  .path=${0}
                  @click=${0}
                  .title=${0}
                >
                </ha-icon-button>
              </div>
            `),this.filterActive?"filter-active":"",this.filterActive?"M21 8H3V6H21V8M13.81 16H10V18H13.09C13.21 17.28 13.46 16.61 13.81 16M18 11H6V13H18V11M21.12 15.46L19 17.59L16.88 15.46L15.47 16.88L17.59 19L15.47 21.12L16.88 22.54L19 20.41L21.12 22.54L22.54 21.12L20.41 19L22.54 16.88L21.12 15.46Z":"M6,13H18V11H6M3,6V8H21V6M10,18H14V16H10V18Z",this._handleFilterClick,this.knx.localize(this.filterActive?"knx_table_cell_filterable_filter_remove_tooltip":"knx_table_cell_filterable_filter_set_tooltip",{value:this.filterDisplayText||this.filterValue})):r.s6)}_handleFilterClick(e){e.stopPropagation(),this.dispatchEvent(new CustomEvent("toggle-filter",{bubbles:!0,composed:!0,detail:{value:this.filterValue,active:!this.filterActive}})),this.filterActive=!this.filterActive}constructor(...e){super(...e),this.filterActive=!1,this.filterDisabled=!1}}h.styles=[...n._.styles,(0,r.AH)(d||(d=c`
      .filter-button {
        display: none;
        flex-shrink: 0;
      }
      .container:hover .filter-button {
        display: block;
      }
      .filter-active {
        display: block;
        color: var(--primary-color);
      }
    `))],(0,o.__decorate)([(0,s.MZ)({type:Object})],h.prototype,"knx",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"filterValue",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"filterDisplayText",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"filterActive",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"filterDisabled",void 0),h=(0,o.__decorate)([(0,s.EM)("knx-table-cell-filterable")],h)},62754:function(e,t,i){i.d(t,{_:function(){return d}});var o=i(69868),r=i(84922),s=i(11991);let n,a,l=e=>e;class d extends r.WF{render(){return(0,r.qy)(n||(n=l`
      <div class="container">
        <div class="content-wrapper">
          <slot name="primary"></slot>
          <slot name="secondary"></slot>
        </div>
      </div>
    `))}}d.styles=[(0,r.AH)(a||(a=l`
      :host {
        display: var(--knx-table-cell-display, block);
      }
      .container {
        padding: 4px 0;
        display: flex;
        align-items: center;
        flex-direction: row;
      }
      .content-wrapper {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
      }
      ::slotted(*) {
        overflow: hidden;
        text-overflow: ellipsis;
      }
      ::slotted(.primary) {
        font-weight: 500;
        margin-bottom: 2px;
      }
      ::slotted(.secondary) {
        color: var(--secondary-text-color);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    `))],d=(0,o.__decorate)([(0,s.EM)("knx-table-cell")],d)},36876:function(e,t,i){i(46852),i(79827),i(35748),i(99342),i(35058),i(65315),i(837),i(22416),i(37089),i(36874),i(47849),i(18223),i(95013);var o=i(69868),r=i(84922),s=i(11991),n=i(75907),a=i(17747),l=i(13802),d=i(33055),c=(i(71978),i(99741)),h=(i(93672),i(51892),i(95635),i(22298),i(83566)),p=i(73120);const u="asc",g=new Intl.Collator(void 0,{numeric:!0,sensitivity:"base"});let m;class _ extends c.p{}_.styles=(0,r.AH)(m||(m=(e=>e)`
    /* Inherit base styles */
    ${0}

    /* Add specific styles for flex content */
    :host {
      display: flex;
      flex-direction: column;
      flex: 1;
      overflow: hidden;
    }

    .container.expanded {
      /* Keep original height: auto from base */
      /* Add requested styles */
      overflow: hidden !important;
      display: flex;
      flex-direction: column;
      flex: 1;
    }
  `),c.p.styles),_=(0,o.__decorate)([(0,s.EM)("flex-content-expansion-panel")],_);i(43143),i(95968),i(25223);let f,b,x,v,y=e=>e;class k extends r.WF{get _ascendingText(){var e,t,i;return null!==(e=null!==(t=this.ascendingText)&&void 0!==t?t:null===(i=this.knx)||void 0===i?void 0:i.localize("knx_sort_menu_item_ascending"))&&void 0!==e?e:""}get _descendingText(){var e,t,i;return null!==(e=null!==(t=this.descendingText)&&void 0!==t?t:null===(i=this.knx)||void 0===i?void 0:i.localize("knx_sort_menu_item_descending"))&&void 0!==e?e:""}render(){return(0,r.qy)(f||(f=y`
      <ha-list-item
        class="sort-row ${0} ${0}"
        @click=${0}
      >
        <div class="container">
          <div class="sort-field-name" title=${0} aria-label=${0}>
            ${0}
          </div>
          <div class="sort-buttons">
            ${0}
          </div>
        </div>
      </ha-list-item>
    `),this.active?"active":"",this.disabled?"disabled":"",this.disabled?r.s6:this._handleItemClick,this.displayName,this.displayName,this.displayName,this.isMobileDevice?this._renderMobileButtons():this._renderDesktopButtons())}_renderMobileButtons(){if(!this.active)return r.s6;const e=this.direction===F.DESC;return(0,r.qy)(b||(b=y`
      <ha-icon-button
        class="active"
        .path=${0}
        .label=${0}
        .title=${0}
        .disabled=${0}
        @click=${0}
      ></ha-icon-button>
    `),e?this.descendingIcon:this.ascendingIcon,e?this._descendingText:this._ascendingText,e?this._descendingText:this._ascendingText,this.disabled,this.disabled?r.s6:this._handleMobileButtonClick)}_renderDesktopButtons(){return(0,r.qy)(x||(x=y`
      <ha-icon-button
        class=${0}
        .path=${0}
        .label=${0}
        .title=${0}
        .disabled=${0}
        @click=${0}
      ></ha-icon-button>
      <ha-icon-button
        class=${0}
        .path=${0}
        .label=${0}
        .title=${0}
        .disabled=${0}
        @click=${0}
      ></ha-icon-button>
    `),this.active&&this.direction===F.DESC?"active":"",this.descendingIcon,this._descendingText,this._descendingText,this.disabled,this.disabled?r.s6:this._handleDescendingClick,this.active&&this.direction===F.ASC?"active":"",this.ascendingIcon,this._ascendingText,this._ascendingText,this.disabled,this.disabled?r.s6:this._handleAscendingClick)}_handleDescendingClick(e){e.stopPropagation(),(0,p.r)(this,"sort-option-selected",{criterion:this.criterion,direction:F.DESC})}_handleAscendingClick(e){e.stopPropagation(),(0,p.r)(this,"sort-option-selected",{criterion:this.criterion,direction:F.ASC})}_handleItemClick(){const e=this.active?this.direction===F.ASC?F.DESC:F.ASC:this.defaultDirection;(0,p.r)(this,"sort-option-selected",{criterion:this.criterion,direction:e})}_handleMobileButtonClick(e){e.stopPropagation();const t=this.direction===F.ASC?F.DESC:F.ASC;(0,p.r)(this,"sort-option-selected",{criterion:this.criterion,direction:t})}constructor(...e){super(...e),this.criterion="idField",this.displayName="",this.defaultDirection=F.DEFAULT_DIRECTION,this.direction=F.ASC,this.active=!1,this.ascendingIcon=k.DEFAULT_ASC_ICON,this.descendingIcon=k.DEFAULT_DESC_ICON,this.isMobileDevice=!1,this.disabled=!1}}k.DEFAULT_ASC_ICON="M13,20H11V8L5.5,13.5L4.08,12.08L12,4.16L19.92,12.08L18.5,13.5L13,8V20Z",k.DEFAULT_DESC_ICON="M11,4H13V16L18.5,10.5L19.92,11.92L12,19.84L4.08,11.92L5.5,10.5L11,16V4Z",k.styles=(0,r.AH)(v||(v=y`
    :host {
      display: block;
    }

    .sort-row {
      display: block;
      padding: 0 16px;
    }

    .sort-row.active {
      --mdc-theme-text-primary-on-background: var(--primary-color);
      background-color: var(--mdc-theme-surface-variant, rgba(var(--rgb-primary-color), 0.06));
      font-weight: 500;
    }

    .sort-row.disabled {
      opacity: 0.6;
      pointer-events: none;
    }

    .sort-row.disabled.active {
      --mdc-theme-text-primary-on-background: var(--primary-color);
      background-color: var(--mdc-theme-surface-variant, rgba(var(--rgb-primary-color), 0.06));
      font-weight: 500;
      opacity: 0.6;
    }

    .container {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      height: 48px;
      gap: 10px;
    }

    .sort-field-name {
      display: flex;
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-size: 1rem;
      align-items: center;
    }

    .sort-buttons {
      display: flex;
      align-items: center;
      min-width: 96px;
      justify-content: flex-end;
    }

    /* Hide sort buttons by default unless active */
    .sort-buttons ha-icon-button:not(.active) {
      display: none;
      color: var(--secondary-text-color);
    }

    /* Show sort buttons on row hover */
    .sort-row:hover .sort-buttons ha-icon-button {
      display: flex;
    }

    /* Don't show hover buttons when disabled */
    .sort-row.disabled:hover .sort-buttons ha-icon-button:not(.active) {
      display: none;
    }

    .sort-buttons ha-icon-button.active {
      display: flex;
      color: var(--primary-color);
    }

    /* Disabled buttons styling */
    .sort-buttons ha-icon-button[disabled] {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .sort-buttons ha-icon-button.active[disabled] {
      --icon-primary-color: var(--primary-color);
      opacity: 0.6;
    }

    /* Mobile device specific styles */
    .sort-buttons ha-icon-button.mobile-button {
      display: flex;
      color: var(--primary-color);
    }
  `)),(0,o.__decorate)([(0,s.MZ)({type:Object})],k.prototype,"knx",void 0),(0,o.__decorate)([(0,s.MZ)({type:String})],k.prototype,"criterion",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"display-name"})],k.prototype,"displayName",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"default-direction"})],k.prototype,"defaultDirection",void 0),(0,o.__decorate)([(0,s.MZ)({type:String})],k.prototype,"direction",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],k.prototype,"active",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"ascending-text"})],k.prototype,"ascendingText",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"descending-text"})],k.prototype,"descendingText",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"ascending-icon"})],k.prototype,"ascendingIcon",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"descending-icon"})],k.prototype,"descendingIcon",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"is-mobile-device"})],k.prototype,"isMobileDevice",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],k.prototype,"disabled",void 0),k=(0,o.__decorate)([(0,s.EM)("knx-sort-menu-item")],k);let $,w,C=e=>e;class F extends r.WF{updated(e){super.updated(e),(e.has("sortCriterion")||e.has("sortDirection")||e.has("isMobileDevice"))&&this._updateMenuItems()}_updateMenuItems(){this._sortMenuItems&&this._sortMenuItems.forEach((e=>{e.active=e.criterion===this.sortCriterion,e.direction=e.criterion===this.sortCriterion?this.sortDirection:e.defaultDirection,e.knx=this.knx,e.isMobileDevice=this.isMobileDevice}))}render(){var e,t;return(0,r.qy)($||($=C`
      <div class="menu-container">
        <ha-menu
          .corner=${0}
          .fixed=${0}
          @opened=${0}
          @closed=${0}
        >
          <slot name="header">
            <div class="header">
              <div class="title">
                <!-- Slot for custom title -->
                <slot name="title">${0}</slot>
              </div>
              <div class="toolbar">
                <!-- Slot for adding custom buttons to the header -->
                <slot name="toolbar"></slot>
              </div>
            </div>
            <li divider></li>
          </slot>

          <!-- Menu items will be slotted here -->
          <slot @sort-option-selected=${0}></slot>
        </ha-menu>
      </div>
    `),"BOTTOM_START",!0,this._handleMenuOpened,this._handleMenuClosed,null!==(e=null===(t=this.knx)||void 0===t?void 0:t.localize("knx_sort_menu_sort_by"))&&void 0!==e?e:"",this._handleSortOptionSelected)}openMenu(e){this._menu&&(this._menu.anchor=e,this._menu.show())}closeMenu(){this._menu&&this._menu.close()}_updateSorting(e,t){e===this.sortCriterion&&t===this.sortDirection||(this.sortCriterion=e,this.sortDirection=t,(0,p.r)(this,"sort-changed",{criterion:e,direction:t}))}_handleMenuOpened(){this._updateMenuItems()}_handleMenuClosed(){}_handleSortOptionSelected(e){const{criterion:t,direction:i}=e.detail;this._updateSorting(t,i),this.closeMenu()}constructor(...e){super(...e),this.sortCriterion="",this.sortDirection=F.DEFAULT_DIRECTION,this.isMobileDevice=!1}}F.ASC="asc",F.DESC="desc",F.DEFAULT_DIRECTION=F.ASC,F.styles=(0,r.AH)(w||(w=C`
    .menu-container {
      position: relative;
      z-index: 1000;
      --mdc-list-vertical-padding: 0;
    }

    .header {
      position: sticky;
      top: 0;
      z-index: 1;
      background-color: var(--card-background-color, #fff);
      border-bottom: 1px solid var(--divider-color);
      font-weight: 500;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      height: 48px;
      gap: 20px;
      width: 100%;
      box-sizing: border-box;
    }

    .header .title {
      font-size: 14px;
      color: var(--secondary-text-color);
      font-weight: 500;
      flex: 1;
    }

    .header .toolbar {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 0px;
    }

    .menu-header .title {
      font-size: 14px;
      color: var(--secondary-text-color);
    }
  `)),(0,o.__decorate)([(0,s.MZ)({type:Object})],F.prototype,"knx",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"sort-criterion"})],F.prototype,"sortCriterion",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"sort-direction"})],F.prototype,"sortDirection",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"is-mobile-device"})],F.prototype,"isMobileDevice",void 0),(0,o.__decorate)([(0,s.P)("ha-menu")],F.prototype,"_menu",void 0),(0,o.__decorate)([(0,s.KN)({selector:"knx-sort-menu-item"})],F.prototype,"_sortMenuItems",void 0),F=(0,o.__decorate)([(0,s.EM)("knx-sort-menu")],F);let T,D,M=e=>e;class S extends r.WF{setHeight(e,t=!0){const i=Math.max(this.minHeight,Math.min(this.maxHeight,e));t?(this._isTransitioning=!0,this.height=i,setTimeout((()=>{this._isTransitioning=!1}),this.animationDuration)):this.height=i}expand(){this.setHeight(this.maxHeight)}collapse(){this.setHeight(this.minHeight)}toggle(){const e=this.minHeight+.5*(this.maxHeight-this.minHeight);this.height<=e?this.expand():this.collapse()}get expansionRatio(){return(this.height-this.minHeight)/(this.maxHeight-this.minHeight)}render(){return(0,r.qy)(T||(T=M`
      <div
        class="separator-container ${0}"
        style="
          height: ${0}px;
          transition: ${0};
        "
      >
        <div class="content">
          <slot></slot>
        </div>
      </div>
    `),this.customClass,this.height,this._isTransitioning?`height ${this.animationDuration}ms ease-in-out`:"none")}constructor(...e){super(...e),this.height=1,this.maxHeight=50,this.minHeight=1,this.animationDuration=150,this.customClass="",this._isTransitioning=!1}}S.styles=(0,r.AH)(D||(D=M`
    :host {
      display: block;
      width: 100%;
      position: relative;
    }

    .separator-container {
      width: 100%;
      overflow: hidden;
      position: relative;
      display: flex;
      flex-direction: column;
      background: var(--card-background-color, var(--primary-background-color));
    }

    .content {
      flex: 1;
      overflow: hidden;
      position: relative;
    }

    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
      .separator-container {
        transition: none !important;
      }
    }
  `)),(0,o.__decorate)([(0,s.MZ)({type:Number,reflect:!0})],S.prototype,"height",void 0),(0,o.__decorate)([(0,s.MZ)({type:Number,attribute:"max-height"})],S.prototype,"maxHeight",void 0),(0,o.__decorate)([(0,s.MZ)({type:Number,attribute:"min-height"})],S.prototype,"minHeight",void 0),(0,o.__decorate)([(0,s.MZ)({type:Number,attribute:"animation-duration"})],S.prototype,"animationDuration",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"custom-class"})],S.prototype,"customClass",void 0),(0,o.__decorate)([(0,s.wk)()],S.prototype,"_isTransitioning",void 0),S=(0,o.__decorate)([(0,s.EM)("knx-separator")],S);let z,A,L,I,H,E,V,O,N,Z,q,j,U,R,P,B,W,K,G,Q,Y=e=>e;class J extends r.WF{_computeFilterSortedOptions(){const e=this._computeFilteredOptions(),t=this._getComparator();return this._sortOptions(e,t,this.sortDirection)}_computeFilterSortedOptionsWithSeparator(){const e=this._computeFilteredOptions(),t=this._getComparator(),i=[],o=[];for(const r of e)r.selected?i.push(r):o.push(r);return{selected:this._sortOptions(i,t,this.sortDirection),unselected:this._sortOptions(o,t,this.sortDirection)}}_computeFilteredOptions(){const{data:e,config:{idField:t,primaryField:i,secondaryField:o,badgeField:r,custom:s},selectedOptions:n=[]}=this,a=e.map((e=>{const a=t.mapper(e),l=i.mapper(e);if(!a||!l)throw new Error("Missing id or primary field on item: "+JSON.stringify(e));const d={idField:a,primaryField:l,secondaryField:o.mapper(e),badgeField:r.mapper(e),selected:n.includes(a)};return s&&Object.entries(s).forEach((([t,i])=>{d[t]=i.mapper(e)})),d}));return this._applyFilterToOptions(a)}_getComparator(){const e=this._getFieldConfig(this.sortCriterion);return null!=e&&e.comparator?e.comparator:this._generateComparator(this.sortCriterion)}_getFieldConfig(e){var t;const{config:i}=this;return e in i&&"custom"!==e?i[e]:null===(t=i.custom)||void 0===t?void 0:t[e]}_generateComparator(e){return(t,i)=>{const o=this._compareByField(t,i,e);return 0!==o?o:this._lazyFallbackComparison(t,i,e)}}_lazyFallbackComparison(e,t,i){const o=this._getFallbackFields(i);for(const r of o){const i=this._compareByField(e,t,r);if(0!==i)return i}return this._compareByField(e,t,"idField")}_getFallbackFields(e){return{idField:[],primaryField:["secondaryField","badgeField"],secondaryField:["primaryField","badgeField"],badgeField:["primaryField","secondaryField"]}[e]||["primaryField"]}_compareByField(e,t,i){var o,r;const s=e[i],n=t[i],a="string"==typeof s?s:null!==(o=null==s?void 0:s.toString())&&void 0!==o?o:"",l="string"==typeof n?n:null!==(r=null==n?void 0:n.toString())&&void 0!==r?r:"";return g.compare(a,l)}firstUpdated(){this._setupSeparatorScrollHandler()}updated(e){(e.has("expanded")||e.has("pinSelectedItems"))&&requestAnimationFrame((()=>{this._setupSeparatorScrollHandler(),(e.has("expanded")&&this.expanded||e.has("pinSelectedItems")&&this.pinSelectedItems)&&requestAnimationFrame((()=>{this._handleSeparatorScroll()}))}))}disconnectedCallback(){super.disconnectedCallback(),this._cleanupSeparatorScrollHandler()}_setupSeparatorScrollHandler(){this._cleanupSeparatorScrollHandler(),this._boundScrollHandler||(this._boundScrollHandler=this._handleSeparatorScroll.bind(this)),this.pinSelectedItems&&this._optionsListContainer&&this._optionsListContainer.addEventListener("scroll",this._boundScrollHandler,{passive:!0})}_cleanupSeparatorScrollHandler(){this._boundScrollHandler&&this._optionsListContainer&&this._optionsListContainer.removeEventListener("scroll",this._boundScrollHandler)}_handleSeparatorScroll(){if(!(this.pinSelectedItems&&this._separator&&this._optionsListContainer&&this._separatorContainer))return;const e=this._optionsListContainer.getBoundingClientRect(),t=this._separatorContainer.getBoundingClientRect().top-e.top,i=this._separatorScrollZone;if(t<=i&&t>=0){const e=1-t/i,o=this._separatorMinHeight+e*(this._separatorMaxHeight-this._separatorMinHeight);this._separator.setHeight(Math.round(o),!1)}else if(t>i){(this._separator.height||this._separatorMinHeight)!==this._separatorMinHeight&&this._separator.setHeight(this._separatorMinHeight,!1)}}_handleSeparatorClick(){this._optionsListContainer&&this._optionsListContainer.scrollTo({top:0,behavior:"smooth"})}_applyFilterToOptions(e){if(!this.filterQuery)return e;const t=this.filterQuery.toLowerCase(),{idField:i,primaryField:o,secondaryField:r,badgeField:s,custom:n}=this.config,a=[];return i.filterable&&a.push((e=>e.idField)),o.filterable&&a.push((e=>e.primaryField)),r.filterable&&a.push((e=>e.secondaryField)),s.filterable&&a.push((e=>e.badgeField)),n&&Object.entries(n).forEach((([e,t])=>{t.filterable&&a.push((t=>{const i=t[e];return"string"==typeof i?i:null==i?void 0:i.toString()}))})),e.filter((e=>a.some((i=>{const o=i(e);return"string"==typeof o&&o.toLowerCase().includes(t)}))))}_sortOptions(e,t,i=u){const o=i===u?1:-1;return[...e].sort(((e,i)=>t(e,i)*o))}_handleSearchChange(e){this.filterQuery=e.detail.value}_handleSortButtonClick(e){var t;e.stopPropagation();const i=null===(t=this.shadowRoot)||void 0===t?void 0:t.querySelector("knx-sort-menu");i&&i.openMenu(e.currentTarget)}_handleSortChanged(e){this.sortCriterion=e.detail.criterion,this.sortDirection=e.detail.direction,(0,p.r)(this,"sort-changed",{criterion:this.sortCriterion,direction:this.sortDirection})}_handlePinButtonClick(e){e.stopPropagation(),this.pinSelectedItems=!this.pinSelectedItems}_handleClearFiltersButtonClick(e){e.stopPropagation(),e.preventDefault(),this._setSelectedOptions([])}_setSelectedOptions(e){this.selectedOptions=e,(0,p.r)(this,"selection-changed",{value:this.selectedOptions})}_getSortIcon(){return this.sortDirection===u?"M3 11H15V13H3M3 18V16H21V18M3 6H9V8H3Z":"M3,13H15V11H3M3,6V8H21V6M3,18H9V16H3V18Z"}_hasFilterableOrSortableFields(){if(!this.config)return!1;return[...Object.values(this.config).filter((e=>e&&"object"==typeof e&&"filterable"in e)),...this.config.custom?Object.values(this.config.custom):[]].some((e=>e.filterable||e.sortable))}_hasFilterableFields(){if(!this.config)return!1;return[...Object.values(this.config).filter((e=>e&&"object"==typeof e&&"filterable"in e)),...this.config.custom?Object.values(this.config.custom):[]].some((e=>e.filterable))}_hasSortableFields(){if(!this.config)return!1;return[...Object.values(this.config).filter((e=>e&&"object"==typeof e&&"sortable"in e)),...this.config.custom?Object.values(this.config.custom):[]].some((e=>e.sortable))}_expandedChanged(e){this.expanded=e.detail.expanded,(0,p.r)(this,"expanded-changed",{expanded:this.expanded})}_handleOptionItemClick(e){const t=e.currentTarget.getAttribute("data-value");t&&this._toggleOption(t)}_toggleOption(e){var t,i,o,r,s;null!==(t=null===(i=this.selectedOptions)||void 0===i?void 0:i.includes(e))&&void 0!==t&&t?this._setSelectedOptions(null!==(o=null===(r=this.selectedOptions)||void 0===r?void 0:r.filter((t=>t!==e)))&&void 0!==o?o:[]):this._setSelectedOptions([...null!==(s=this.selectedOptions)&&void 0!==s?s:[],e]);requestAnimationFrame((()=>{this._handleSeparatorScroll()}))}_renderFilterControl(){var e;return(0,r.qy)(z||(z=Y`
      <div class="filter-toolbar">
        <div class="search">
          ${0}
        </div>
        ${0}
      </div>
    `),this._hasFilterableFields()?(0,r.qy)(A||(A=Y`
                <search-input-outlined
                  .hass=${0}
                  .filter=${0}
                  @value-changed=${0}
                ></search-input-outlined>
              `),this.hass,this.filterQuery,this._handleSearchChange):r.s6,this._hasSortableFields()?(0,r.qy)(L||(L=Y`
              <div class="buttons">
                <ha-icon-button
                  class="sort-button"
                  .path=${0}
                  title=${0}
                  @click=${0}
                ></ha-icon-button>

                <knx-sort-menu
                  .knx=${0}
                  .sortCriterion=${0}
                  .sortDirection=${0}
                  .isMobileDevice=${0}
                  @sort-changed=${0}
                >
                  <div slot="title">${0}</div>

                  <!-- Toolbar with additional controls like pin button -->
                  <div slot="toolbar">
                    <!-- Pin Button for keeping selected items at top -->
                    <ha-icon-button-toggle
                      .path=${0}
                      .selected=${0}
                      @click=${0}
                      title=${0}
                    >
                    </ha-icon-button-toggle>
                  </div>

                  <!-- Sort menu items generated from all sortable fields -->
                  ${0}
                </knx-sort-menu>
              </div>
            `),this._getSortIcon(),this.sortDirection===u?this.knx.localize("knx_list_filter_sort_ascending_tooltip"):this.knx.localize("knx_list_filter_sort_descending_tooltip"),this._handleSortButtonClick,this.knx,this.sortCriterion,this.sortDirection,this.isMobileDevice,this._handleSortChanged,this.knx.localize("knx_list_filter_sort_by"),"M16,12V4H17V2H7V4H8V12L6,14V16H11.2V22H12.8V16H18V14L16,12Z",this.pinSelectedItems,this._handlePinButtonClick,this.knx.localize("knx_list_filter_selected_items_on_top"),[...Object.entries(this.config||{}).filter((([e])=>"custom"!==e)).map((([e,t])=>({key:e,config:t}))),...Object.entries((null===(e=this.config)||void 0===e?void 0:e.custom)||{}).map((([e,t])=>({key:e,config:t})))].filter((({config:e})=>e.sortable)).map((({key:e,config:t})=>{var i,o,s;return(0,r.qy)(I||(I=Y`
                        <knx-sort-menu-item
                          criterion=${0}
                          display-name=${0}
                          default-direction=${0}
                          ascending-text=${0}
                          descending-text=${0}
                          .disabled=${0}
                        ></knx-sort-menu-item>
                      `),e,(0,l.J)(t.fieldName),null!==(i=t.sortDefaultDirection)&&void 0!==i?i:"asc",null!==(o=t.sortAscendingText)&&void 0!==o?o:this.knx.localize("knx_list_filter_sort_ascending"),null!==(s=t.sortDescendingText)&&void 0!==s?s:this.knx.localize("knx_list_filter_sort_descending"),t.sortDisabled||!1)}))):r.s6)}_renderOptionsList(){return(0,r.qy)(H||(H=Y`
      ${0}
    `),(0,a.a)([this.filterQuery,this.sortDirection,this.sortCriterion,this.data,this.selectedOptions,this.expanded,this.config,this.pinSelectedItems],(()=>this.pinSelectedItems?this._renderPinnedOptionsList():this._renderRegularOptionsList())))}_renderPinnedOptionsList(){var e;const t=this.knx.localize("knx_list_filter_no_results"),{selected:i,unselected:o}=this._computeFilterSortedOptionsWithSeparator();return 0===i.length&&0===o.length?(0,r.qy)(E||(E=Y`<div class="empty-message" role="alert">${0}</div>`),t):(0,r.qy)(V||(V=Y`
      <div class="options-list" tabindex="0">
        <!-- Render selected items first -->
        ${0}

        <!-- Render separator between selected and unselected items -->
        ${0}

        <!-- Render unselected items -->
        ${0}
      </div>
    `),i.length>0?(0,r.qy)(O||(O=Y`
              ${0}
            `),(0,d.u)(i,(e=>e.idField),(e=>this._renderOptionItem(e)))):r.s6,i.length>0&&o.length>0?(0,r.qy)(N||(N=Y`
              <div class="separator-container">
                <knx-separator
                  .height=${0}
                  .maxHeight=${0}
                  .minHeight=${0}
                  .animationDuration=${0}
                  customClass="list-separator"
                >
                  <div class="separator-content" @click=${0}>
                    <ha-svg-icon .path=${0}></ha-svg-icon>
                    <span class="separator-text">
                      ${0}
                    </span>
                  </div>
                </knx-separator>
              </div>
            `),(null===(e=this._separator)||void 0===e?void 0:e.height)||this._separatorMinHeight,this._separatorMaxHeight,this._separatorMinHeight,this._separatorAnimationDuration,this._handleSeparatorClick,"M7.41,15.41L12,10.83L16.59,15.41L18,14L12,8L6,14L7.41,15.41Z",this.knx.localize("knx_list_filter_scroll_to_selection")):r.s6,o.length>0?(0,r.qy)(Z||(Z=Y`
              ${0}
            `),(0,d.u)(o,(e=>e.idField),(e=>this._renderOptionItem(e)))):r.s6)}_renderRegularOptionsList(){const e=this.knx.localize("knx_list_filter_no_results"),t=this._computeFilterSortedOptions();return 0===t.length?(0,r.qy)(q||(q=Y`<div class="empty-message" role="alert">${0}</div>`),e):(0,r.qy)(j||(j=Y`
      <div class="options-list" tabindex="0">
        ${0}
      </div>
    `),(0,d.u)(t,(e=>e.idField),(e=>this._renderOptionItem(e))))}_renderOptionItem(e){const t={"option-item":!0,selected:e.selected};return(0,r.qy)(U||(U=Y`
      <div
        class=${0}
        role="option"
        aria-selected=${0}
        @click=${0}
        data-value=${0}
      >
        <div class="option-content">
          <div class="option-primary">
            <span class="option-label" title=${0}>${0}</span>
            ${0}
          </div>

          ${0}
        </div>

        <ha-checkbox
          .checked=${0}
          .value=${0}
          tabindex="-1"
          pointer-events="none"
        ></ha-checkbox>
      </div>
    `),(0,n.H)(t),e.selected,this._handleOptionItemClick,e.idField,e.primaryField,e.primaryField,e.badgeField?(0,r.qy)(R||(R=Y`<span class="option-badge">${0}</span>`),e.badgeField):r.s6,e.secondaryField?(0,r.qy)(P||(P=Y`
                <div class="option-secondary" title=${0}>
                  ${0}
                </div>
              `),e.secondaryField,e.secondaryField):r.s6,e.selected,e.idField)}render(){var e,t;const i=null!==(e=null===(t=this.selectedOptions)||void 0===t?void 0:t.length)&&void 0!==e?e:0,o=this.filterTitle||this.knx.localize("knx_list_filter_title"),s=this.knx.localize("knx_list_filter_clear");return(0,r.qy)(B||(B=Y`
      <flex-content-expansion-panel
        leftChevron
        .expanded=${0}
        @expanded-changed=${0}
      >
        <!-- Header with title and clear selection control -->
        <div slot="header" class="header">
          <span class="title">
            ${0}
            ${0}
          </span>
          <div class="controls">
            ${0}
          </div>
        </div>

        <!-- Render filter content only when panel is expanded and visible -->
        ${0}
      </flex-content-expansion-panel>
    `),this.expanded,this._expandedChanged,o,i?(0,r.qy)(W||(W=Y`<div class="badge">${0}</div>`),i):r.s6,i?(0,r.qy)(K||(K=Y`
                  <ha-icon-button
                    .path=${0}
                    @click=${0}
                    .title=${0}
                  ></ha-icon-button>
                `),"M21 8H3V6H21V8M13.81 16H10V18H13.09C13.21 17.28 13.46 16.61 13.81 16M18 11H6V13H18V11M21.12 15.46L19 17.59L16.88 15.46L15.47 16.88L17.59 19L15.47 21.12L16.88 22.54L19 20.41L21.12 22.54L22.54 21.12L20.41 19L22.54 16.88L21.12 15.46Z",this._handleClearFiltersButtonClick,s):r.s6,this.expanded?(0,r.qy)(G||(G=Y`
              <div class="filter-content">
                ${0}
              </div>

              <!-- Filter options list - moved outside filter-content for proper sticky behavior -->
              <div class="options-list-wrapper ha-scrollbar">${0}</div>
            `),this._hasFilterableOrSortableFields()?this._renderFilterControl():r.s6,this._renderOptionsList()):r.s6)}static get styles(){return[h.dp,(0,r.AH)(Q||(Q=Y`
        :host {
          display: flex;
          flex-direction: column;
          border-bottom: 1px solid var(--divider-color);
        }
        :host([expanded]) {
          flex: 1;
          height: 0;
          overflow: hidden;
        }

        flex-content-expansion-panel {
          --ha-card-border-radius: 0;
          --expansion-panel-content-padding: 0;
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          width: 100%;
        }

        .title {
          display: flex;
          align-items: center;
          font-weight: 500;
        }

        .badge {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          margin-left: 8px;
          min-width: 20px;
          height: 20px;
          box-sizing: border-box;
          border-radius: 50%;
          font-weight: 500;
          font-size: 12px;
          background-color: var(--primary-color);
          line-height: 1;
          text-align: center;
          padding: 0 4px;
          color: var(--text-primary-color);
        }

        .controls {
          display: flex;
          align-items: center;
          margin-left: auto;
        }

        .header ha-icon-button {
          margin-inline-end: 4px;
        }

        .filter-content {
          display: flex;
          flex-direction: column;
          flex-shrink: 0;
        }

        .options-list-wrapper {
          flex: 1;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
        }

        .options-list {
          display: block;
          padding: 0;
          flex: 1;
        }

        .filter-toolbar {
          display: flex;
          align-items: center;
          padding: 0px 8px;
          gap: 4px;
          border-bottom: 1px solid var(--divider-color);
        }

        .search {
          flex: 1;
        }

        .buttons:last-of-type {
          margin-right: -8px;
        }

        search-input-outlined {
          display: block;
          flex: 1;
          padding: 8px 0;
        }

        .option-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding-left: 16px;
          min-height: 48px;
          cursor: pointer;
          position: relative;
        }
        .option-item:hover {
          background-color: rgba(var(--rgb-primary-text-color), 0.04);
        }
        .option-item.selected {
          background-color: var(--mdc-theme-surface-variant, rgba(var(--rgb-primary-color), 0.06));
        }

        .option-content {
          display: flex;
          flex-direction: column;
          width: 100%;
          min-width: 0;
          height: 100%;
          line-height: normal;
        }

        .option-primary {
          display: flex;
          justify-content: space-between;
          align-items: center;
          width: 100%;
          margin-bottom: 3px;
        }

        .option-label {
          font-weight: 500;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .option-secondary {
          color: var(--secondary-text-color);
          font-size: 0.85em;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .option-badge {
          display: inline-flex;
          background-color: rgba(var(--rgb-primary-color), 0.15);
          color: var(--primary-color);
          font-weight: 500;
          font-size: 0.75em;
          padding: 1px 6px;
          border-radius: 10px;
          min-width: 20px;
          height: 16px;
          align-items: center;
          justify-content: center;
          margin-left: 8px;
          vertical-align: middle;
        }

        .empty-message {
          text-align: center;
          padding: 16px;
          color: var(--secondary-text-color);
        }

        /* Prevent checkbox from capturing clicks */
        ha-checkbox {
          pointer-events: none;
        }

        knx-sort-menu ha-icon-button-toggle {
          --mdc-icon-button-size: 36px; /* Default is 48px */
          --mdc-icon-size: 18px; /* Default is 24px */
          color: var(--secondary-text-color);
        }

        knx-sort-menu ha-icon-button-toggle[selected] {
          --primary-background-color: var(--primary-color);
          --primary-text-color: transparent;
        }

        /* Separator Styling */
        .separator-container {
          position: sticky;
          top: 0;
          z-index: 10;
          background: var(--card-background-color);
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .separator-content {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100%;
          gap: 6px;
          padding: 8px;
          background: var(--primary-color);
          color: var(--text-primary-color);
          font-size: 0.8em;
          font-weight: 500;
          cursor: pointer;
          transition: opacity 0.2s ease;
          user-select: none;
          box-sizing: border-box;
        }

        .separator-content:hover {
          opacity: 0.9;
        }

        .separator-content ha-svg-icon {
          --mdc-icon-size: 16px;
        }

        .separator-text {
          text-align: center;
        }

        .list-separator {
          position: relative;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        /* Enhanced separator visibility when scrolled */
        .options-list:not(:hover) .separator-container {
          transition: box-shadow 0.2s ease;
        }
      `))]}constructor(...e){super(...e),this.data=[],this.expanded=!1,this.narrow=!1,this.pinSelectedItems=!0,this.filterQuery="",this.sortCriterion="primaryField",this.sortDirection="asc",this.isMobileDevice=!1,this._separatorMaxHeight=28,this._separatorMinHeight=2,this._separatorAnimationDuration=150,this._separatorScrollZone=28}}(0,o.__decorate)([(0,s.MZ)({attribute:!1,hasChanged:()=>!1})],J.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],J.prototype,"knx",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],J.prototype,"data",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],J.prototype,"selectedOptions",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],J.prototype,"config",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0})],J.prototype,"expanded",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],J.prototype,"narrow",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"pin-selected-items"})],J.prototype,"pinSelectedItems",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"filter-title"})],J.prototype,"filterTitle",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"filter-query"})],J.prototype,"filterQuery",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"sort-criterion"})],J.prototype,"sortCriterion",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"sort-direction"})],J.prototype,"sortDirection",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"is-mobile-device"})],J.prototype,"isMobileDevice",void 0),(0,o.__decorate)([(0,s.P)("knx-separator")],J.prototype,"_separator",void 0),(0,o.__decorate)([(0,s.P)(".options-list-wrapper")],J.prototype,"_optionsListContainer",void 0),(0,o.__decorate)([(0,s.P)(".separator-container")],J.prototype,"_separatorContainer",void 0),J=(0,o.__decorate)([(0,s.EM)("knx-list-filter")],J)},40442:function(e,t,i){i(35748),i(95013);var o=i(69868),r=i(84922),s=i(11991);let n,a,l=e=>e;class d extends r.WF{render(){return(0,r.qy)(n||(n=l`
      <header class="header">
        <div class="header-bar">
          <section class="header-navigation-icon">
            <slot name="navigationIcon"></slot>
          </section>
          <section class="header-content">
            <div class="header-title">
              <slot name="title"></slot>
            </div>
            <div class="header-subtitle">
              <slot name="subtitle"></slot>
            </div>
          </section>
          <section class="header-action-items">
            <slot name="actionItems"></slot>
          </section>
        </div>
        <slot></slot>
      </header>
    `))}static get styles(){return[(0,r.AH)(a||(a=l`
        :host {
          display: block;
        }
        :host([show-border]) {
          border-bottom: 1px solid var(--mdc-dialog-scroll-divider-color, rgba(0, 0, 0, 0.12));
        }
        .header-bar {
          display: flex;
          flex-direction: row;
          align-items: center;
          padding: 4px 24px 4px 24px;
          box-sizing: border-box;
          gap: 12px;
        }
        .header-content {
          flex: 1;
          padding: 10px 4px;
          min-width: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .header-title {
          font-size: 22px;
          line-height: 28px;
          font-weight: 400;
        }
        .header-subtitle {
          margin-top: 2px;
          font-size: 14px;
          color: var(--secondary-text-color);
        }

        .header-navigation-icon {
          flex: none;
          min-width: 8px;
          height: 100%;
          display: flex;
          flex-direction: row;
        }
        .header-action-items {
          flex: none;
          min-width: 8px;
          height: 100%;
          display: flex;
          flex-direction: row;
        }
      `))]}constructor(...e){super(...e),this.showBorder=!1}}(0,o.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0,attribute:"show-border"})],d.prototype,"showBorder",void 0),d=(0,o.__decorate)([(0,s.EM)("knx-dialog-header")],d)},62620:function(e,t,i){i.d(t,{K:function(){return _}});i(46852),i(79827),i(35748),i(35058),i(65315),i(12840),i(837),i(22416),i(37089),i(36874),i(12977),i(5934),i(67579),i(47849),i(18223),i(79566),i(95013),i(13484),i(81071),i(92714),i(55885);var o=i(68985),r=i(90933),s=i(65940),n=i(49432);i(99342),i(84136),i(88238),i(34536),i(16257),i(20152),i(44711),i(72108),i(77030);class a{add(e){const t=Array.isArray(e)?e:[e];if(0===this._buffer.length)this._buffer.push(...t),t.length>1&&this._buffer.sort(((e,t)=>e.timestampIso<t.timestampIso?-1:e.timestampIso>t.timestampIso?1:0));else{const e=this._buffer[this._buffer.length-1].timestampIso,i=t.every((t=>t.timestampIso>=e)),o=t.length<=1||t.every(((e,i)=>0===i||t[i-1].timestampIso<=e.timestampIso));i&&o?this._buffer.push(...t):(this._buffer.push(...t),this._buffer.sort(((e,t)=>e.timestampIso<t.timestampIso?-1:e.timestampIso>t.timestampIso?1:0)))}if(this._buffer.length>this._maxSize){const e=this._buffer.length-this._maxSize;return this._buffer.splice(0,e)}return[]}merge(e){const t=new Set(this._buffer.map((e=>e.id))),i=e.filter((e=>!t.has(e.id)));i.sort(((e,t)=>e.timestampIso<t.timestampIso?-1:e.timestampIso>t.timestampIso?1:0));return{added:i,removed:this.add(i)}}setMaxSize(e){if(this._maxSize=e,this._buffer.length>e){const t=this._buffer.length-e;return this._buffer.splice(0,t)}return[]}get maxSize(){return this._maxSize}get length(){return this._buffer.length}get snapshot(){return[...this._buffer]}clear(){const e=[...this._buffer];return this._buffer.length=0,e}get isEmpty(){return 0===this._buffer.length}at(e){return this._buffer[e]}findIndexById(e){return this._buffer.findIndex((t=>t.id===e))}getById(e){return this._buffer.find((t=>t.id===e))}constructor(e=2e3){this._maxSize=e,this._buffer=[]}}var l=i(92095);const d=new l.Q("connection_service");class c{get connectionError(){return this._connectionError}get isConnected(){return!!this._subscribed}onTelegram(e){this._onTelegram=e}onConnectionChange(e){this._onConnectionChange=e}async subscribe(e){if(this._subscribed)d.warn("Already subscribed to telegrams");else try{this._subscribed=await(0,n.EE)(e,(e=>{this._onTelegram&&this._onTelegram(e)})),this._connectionError=null,this._notifyConnectionChange(!0),d.debug("Successfully subscribed to telegrams")}catch(t){throw d.error("Failed to subscribe to telegrams",t),this._connectionError=t instanceof Error?t.message:String(t),this._notifyConnectionChange(!1,this._connectionError),t}}unsubscribe(){this._subscribed&&(this._subscribed(),this._subscribed=void 0,this._notifyConnectionChange(!1),d.debug("Unsubscribed from telegrams"))}async reconnect(e){this._connectionError=null,this._notifyConnectionChange(!1),await this.subscribe(e)}clearError(){this._connectionError=null,this._notifyConnectionChange(this.isConnected)}disconnect(){this.unsubscribe(),this._onTelegram=null,this._onConnectionChange=null}_notifyConnectionChange(e,t){this._onConnectionChange&&this._onConnectionChange(e,t)}constructor(){this._connectionError=null,this._onTelegram=null,this._onConnectionChange=null}}var h=i(85735),p=i(93060);class u{constructor(e){this.offset=null,this.id=(0,h.Y)(`${e.timestamp}_${e.source}_${e.destination}`),this.timestampIso=e.timestamp,this.timestamp=new Date(e.timestamp),this.sourceAddress=e.source,this.sourceText=e.source_name,this.sourceName=`${e.source}: ${e.source_name}`,this.destinationAddress=e.destination,this.destinationText=e.destination_name,this.destinationName=`${e.destination}: ${e.destination_name}`,this.type=e.telegramtype,this.direction=e.direction,this.payload=p.e4.payload(e),this.dpt=p.e4.dptNameNumber(e),this.unit=e.unit,this.value=p.e4.valueWithUnit(e)||this.payload||("GroupValueRead"===e.telegramtype?"GroupRead":"")}}const g=new l.Q("group_monitor_controller"),m=["source","destination","direction","telegramtype"];class _{hostConnected(){this._setFiltersFromUrl()}hostDisconnected(){this._connectionService.disconnect()}async setup(e){if(!this._connectionService.isConnected&&await this._loadRecentTelegrams(e))try{await this._connectionService.subscribe(e)}catch(t){g.error("Failed to setup connection",t),this._connectionError=t instanceof Error?t.message:String(t),this.host.requestUpdate()}}get telegrams(){return this._telegramBuffer.snapshot}get selectedTelegramId(){return this._selectedTelegramId}set selectedTelegramId(e){this._selectedTelegramId=e,this.host.requestUpdate()}get filters(){return this._filters}get sortColumn(){return this._sortColumn}set sortColumn(e){this._sortColumn=e,this.host.requestUpdate()}get sortDirection(){return this._sortDirection}set sortDirection(e){this._sortDirection=e||"desc",this.host.requestUpdate()}get expandedFilter(){return this._expandedFilter}get isReloadEnabled(){return this._isReloadEnabled}get isPaused(){return this._isPaused}get isProjectLoaded(){return this._isProjectLoaded}get connectionError(){return this._connectionError}getFilteredTelegramsAndDistinctValues(){return this._getFilteredTelegramsAndDistinctValues(this._bufferVersion,JSON.stringify(this._filters),this._telegramBuffer.snapshot,this._distinctValues,this._sortColumn,this._sortDirection)}matchesActiveFilters(e){return Object.entries(this._filters).every((([t,i])=>{if(null==i||!i.length)return!0;const o={source:e.sourceAddress,destination:e.destinationAddress,direction:e.direction,telegramtype:e.type};return i.includes(o[t]||"")}))}toggleFilterValue(e,t,i){var o;const r=null!==(o=this._filters[e])&&void 0!==o?o:[];r.includes(t)?this._filters=Object.assign(Object.assign({},this._filters),{},{[e]:r.filter((e=>e!==t))}):this._filters=Object.assign(Object.assign({},this._filters),{},{[e]:[...r,t]}),this._updateUrlFromFilters(i),this._cleanupUnusedFilterValues(),this.host.requestUpdate()}setFilterFieldValue(e,t,i){this._filters=Object.assign(Object.assign({},this._filters),{},{[e]:t}),this._updateUrlFromFilters(i),this._cleanupUnusedFilterValues(),this.host.requestUpdate()}clearFilters(e){this._filters={},this._updateUrlFromFilters(e),this._cleanupUnusedFilterValues(),this.host.requestUpdate()}updateExpandedFilter(e,t){this._expandedFilter=t?e:this._expandedFilter===e?null:this._expandedFilter,this.host.requestUpdate()}async togglePause(){this._isPaused=!this._isPaused,this.host.requestUpdate()}async reload(e){await this._loadRecentTelegrams(e)}async retryConnection(e){await this._connectionService.reconnect(e)}clearTelegrams(){const e=this._createFilteredDistinctValues();this._telegramBuffer.clear(),this._resetDistinctValues(e),this._isReloadEnabled=!0,this.host.requestUpdate()}navigateTelegram(e,t){if(!this._selectedTelegramId)return;const i=t.findIndex((e=>e.id===this._selectedTelegramId))+e;i>=0&&i<t.length&&(this._selectedTelegramId=t[i].id,this.host.requestUpdate())}_calculateTelegramOffset(e,t){if(!t)return null;return(0,p.u_)(e.timestampIso)-(0,p.u_)(t.timestampIso)}_extractTelegramField(e,t){switch(t){case"source":return{id:e.sourceAddress,name:e.sourceText||""};case"destination":return{id:e.destinationAddress,name:e.destinationText||""};case"direction":return{id:e.direction,name:""};case"telegramtype":return{id:e.type,name:""};default:return null}}_addToDistinctValues(e){for(const t of m){const i=this._extractTelegramField(e,t);if(!i){g.warn(`Unknown field for distinct values: ${t}`);continue}const{id:o,name:r}=i;this._distinctValues[t][o]||(this._distinctValues[t][o]={id:o,name:r,totalCount:0}),this._distinctValues[t][o].totalCount++,""===this._distinctValues[t][o].name&&r&&(this._distinctValues[t][o].name=r)}this._bufferVersion++}_removeFromDistinctValues(e){if(0!==e.length){for(const t of e)for(const e of m){const i=this._extractTelegramField(t,e);if(!i)continue;const{id:o}=i,r=this._distinctValues[e][o];r&&(r.totalCount--,r.totalCount<=0&&delete this._distinctValues[e][o])}this._bufferVersion++}}_createFilteredDistinctValues(){const e={source:{},destination:{},direction:{},telegramtype:{}};for(const t of m){const i=this._filters[t];if(null!=i&&i.length)for(const o of i){const i=this._distinctValues[t][o];e[t][o]={id:o,name:(null==i?void 0:i.name)||"",totalCount:0}}}return e}_cleanupUnusedFilterValues(){let e=!1;for(const t of m){const i=this._filters[t]||[],o=this._distinctValues[t];for(const[r,s]of Object.entries(o))0!==s.totalCount||i.includes(r)||(delete this._distinctValues[t][r],e=!0)}e&&this._bufferVersion++}_resetDistinctValues(e){this._distinctValues=e?{source:Object.assign({},e.source),destination:Object.assign({},e.destination),direction:Object.assign({},e.direction),telegramtype:Object.assign({},e.telegramtype)}:{source:{},destination:{},direction:{},telegramtype:{}},this._bufferVersion++}_calculateTelegramStorageBuffer(e){const t=Math.ceil(.1*e),i=100*Math.ceil(t/100);return Math.max(i,_.MIN_TELEGRAM_STORAGE_BUFFER)}async _loadRecentTelegrams(e){try{const t=await(0,n.eq)(e);this._isProjectLoaded=t.project_loaded;const i=t.recent_telegrams.length,o=i+this._calculateTelegramStorageBuffer(i);if(this._telegramBuffer.maxSize!==o){const e=this._telegramBuffer.setMaxSize(o);e.length>0&&this._removeFromDistinctValues(e)}const r=t.recent_telegrams.map((e=>new u(e))),{added:s,removed:a}=this._telegramBuffer.merge(r);if(a.length>0&&this._removeFromDistinctValues(a),s.length>0)for(const e of s)this._addToDistinctValues(e);return null!==this._connectionError&&(this._connectionError=null),this._isReloadEnabled=!1,(s.length>0||null===this._connectionError)&&this.host.requestUpdate(),!0}catch(t){return g.error("getGroupMonitorInfo failed",t),this._connectionError=t instanceof Error?t.message:String(t),this.host.requestUpdate(),!1}}_handleIncomingTelegram(e){const t=new u(e);if(this._isPaused)this._isReloadEnabled||(this._isReloadEnabled=!0,this.host.requestUpdate());else{const e=this._telegramBuffer.add(t);e.length>0&&this._removeFromDistinctValues(e),this._addToDistinctValues(t),this.host.requestUpdate()}}_updateUrlFromFilters(e){if(!e)return void g.warn("Route not available, cannot update URL");const t=new URLSearchParams;Object.entries(this._filters).forEach((([e,i])=>{Array.isArray(i)&&i.length>0&&t.set(e,i.join(","))}));const i=t.toString()?`${e.prefix}${e.path}?${t.toString()}`:`${e.prefix}${e.path}`;(0,o.o)(decodeURIComponent(i),{replace:!0})}_setFiltersFromUrl(){const e=new URLSearchParams(r.G.location.search),t=e.get("source"),i=e.get("destination"),o=e.get("direction"),s=e.get("telegramtype");if(!(t||i||o||s))return;this._filters={source:t?t.split(","):[],destination:i?i.split(","):[],direction:o?o.split(","):[],telegramtype:s?s.split(","):[]};const n=this._createFilteredDistinctValues();this._resetDistinctValues(n),this.host.requestUpdate()}constructor(e){this._connectionService=new c,this._telegramBuffer=new a(2e3),this._selectedTelegramId=null,this._filters={},this._sortColumn="timestampIso",this._sortDirection="desc",this._expandedFilter="source",this._isReloadEnabled=!1,this._isPaused=!1,this._isProjectLoaded=void 0,this._connectionError=null,this._distinctValues={source:{},destination:{},direction:{},telegramtype:{}},this._bufferVersion=0,this._getFilteredTelegramsAndDistinctValues=(0,s.A)(((e,t,i,o,r,s)=>{const n=i.filter((e=>this.matchesActiveFilters(e)));r&&s&&n.sort(((e,t)=>{let i,o,n;switch(r){case"timestampIso":i=e.timestampIso,o=t.timestampIso;break;case"sourceAddress":i=e.sourceAddress,o=t.sourceAddress;break;case"destinationAddress":i=e.destinationAddress,o=t.destinationAddress;break;case"sourceText":i=e.sourceText||"",o=t.sourceText||"";break;case"destinationText":i=e.destinationText||"",o=t.destinationText||"";break;default:i=e[r]||"",o=t[r]||""}return n="string"==typeof i&&"string"==typeof o?i.localeCompare(o):i<o?-1:i>o?1:0,"asc"===s?n:-n}));const a={source:{},destination:{},direction:{},telegramtype:{}},l=Object.keys(o);for(const d of l)for(const[e,t]of Object.entries(o[d]))a[d][e]={id:t.id,name:t.name,totalCount:t.totalCount,filteredCount:0};for(let d=0;d<n.length;d++){const e=n[d];if("timestampIso"===r&&s||!r){let t=null;t="desc"===s&&r?d<n.length-1?n[d+1]:null:d>0?n[d-1]:null,e.offset=this._calculateTelegramOffset(e,t)}else e.offset=null;for(const t of l){const i=this._extractTelegramField(e,t);if(!i)continue;const{id:o}=i,r=a[t][o];r&&(r.filteredCount=(r.filteredCount||0)+1)}}return{filteredTelegrams:n,distinctValues:a}})),this.host=e,e.addController(this),this._connectionService.onTelegram((e=>this._handleIncomingTelegram(e))),this._connectionService.onConnectionChange(((e,t)=>{this._connectionError=t||null,this.host.requestUpdate()}))}}_.MIN_TELEGRAM_STORAGE_BUFFER=1e3},31123:function(e,t,i){i.a(e,(async function(e,t){try{i(35748),i(95013);var o=i(69868),r=i(84922),s=i(11991),n=i(73120),a=i(83566),l=(i(95635),i(76943)),d=(i(40442),i(93060)),c=i(21873),h=(i(93672),i(72847),e([l,c]));[l,c]=h.then?(await h)():h;let p,u,g,m,_,f,b,x=e=>e;const v="M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z",y="M4,11V13H16L10.5,18.5L11.92,19.92L19.84,12L11.92,4.08L10.5,5.5L16,11H4Z",k="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z";class $ extends r.WF{connectedCallback(){super.connectedCallback(),this._handleKeyDown=this._handleKeyDown.bind(this),document.addEventListener("keydown",this._handleKeyDown)}disconnectedCallback(){document.removeEventListener("keydown",this._handleKeyDown),super.disconnectedCallback()}closeDialog(){this.telegram=void 0,(0,n.r)(this,"dialog-closed",{dialog:this.localName},{bubbles:!1})}_checkScrolled(e){var t;const i=e.target,o=null===(t=this.shadowRoot)||void 0===t?void 0:t.querySelector("knx-dialog-header");o&&i.scrollTop>0?o.showBorder=!0:o&&(o.showBorder=!1)}render(){if(!this.telegram)return this.closeDialog(),r.s6;const e="Outgoing"===this.telegram.direction?"outgoing":"incoming";return(0,r.qy)(p||(p=x`
      <!-- 
        The .heading property is required for the header slot to be rendered,
        even though we override it with our custom knx-dialog-header component.
        The value is not displayed but must be truthy for the slot to work.
      -->
      <ha-dialog open @closed=${0} .heading=${0}>
        <knx-dialog-header slot="heading" .showBorder=${0}>
          <ha-icon-button
            slot="navigationIcon"
            .label=${0}
            .path=${0}
            dialogAction="close"
            class="close-button"
          ></ha-icon-button>
          <div slot="title" class="header-title">
            ${0}
          </div>
          <div slot="subtitle">
            <span title=${0}>
              ${0}
            </span>
            ${0}
          </div>
          <div slot="actionItems" class="direction-badge ${0}">
            ${0}
          </div>
        </knx-dialog-header>
        <div class="content" @scroll=${0}>
          <!-- Body: addresses + value + details -->
          <div class="telegram-body">
            <div class="addresses-row">
              <div class="address-item">
                <div class="item-label">
                  ${0}
                </div>
                <div class="address-chip">${0}</div>
                ${0}
              </div>
              <div class="address-item">
                <div class="item-label">
                  ${0}
                </div>
                <div class="address-chip">${0}</div>
                ${0}
              </div>
            </div>

            ${0}

            <div class="telegram-details">
              <div class="detail-grid">
                <div class="detail-item">
                  <div class="detail-label">
                    ${0}
                  </div>
                  <div class="detail-value">${0}</div>
                </div>
                <div class="detail-item">
                  <div class="detail-label">DPT</div>
                  <div class="detail-value">${0}</div>
                </div>
                ${0}
              </div>
            </div>
          </div>
        </div>

        <!-- Navigation buttons: previous / next -->
        <div slot="secondaryAction">
          <ha-button
            appearance="plain"
            @click=${0}
            .disabled=${0}
          >
            <ha-svg-icon .path=${0} slot="start"></ha-svg-icon>
            ${0}
          </ha-button>
        </div>
        <div slot="primaryAction" class="primaryAction">
          <ha-button appearance="plain" @click=${0} .disabled=${0}>
            ${0}
            <ha-svg-icon .path=${0} slot="end"></ha-svg-icon>
          </ha-button>
        </div>
      </ha-dialog>
    `),this.closeDialog," ",!0,this.knx.localize("ui.dialogs.generic.close"),k,this.knx.localize("knx_telegram_info_dialog_telegram"),(0,d.CY)(this.telegram.timestampIso),(0,d.HF)(this.telegram.timestamp)+" ",this.narrow?r.s6:(0,r.qy)(u||(u=x`
                  (<ha-relative-time
                    .hass=${0}
                    .datetime=${0}
                    .capitalize=${0}
                  ></ha-relative-time
                  >)
                `),this.hass,this.telegram.timestamp,!1),e,this.knx.localize(this.telegram.direction),this._checkScrolled,this.knx.localize("knx_telegram_info_dialog_source"),this.telegram.sourceAddress,this.telegram.sourceText?(0,r.qy)(g||(g=x`<div class="item-name">${0}</div>`),this.telegram.sourceText):r.s6,this.knx.localize("knx_telegram_info_dialog_destination"),this.telegram.destinationAddress,this.telegram.destinationText?(0,r.qy)(m||(m=x`<div class="item-name">${0}</div>`),this.telegram.destinationText):r.s6,null!=this.telegram.value?(0,r.qy)(_||(_=x`
                  <div class="value-section">
                    <div class="value-label">
                      ${0}
                    </div>
                    <div class="value-content">${0}</div>
                  </div>
                `),this.knx.localize("knx_telegram_info_dialog_value"),this.telegram.value):r.s6,this.knx.localize("knx_telegram_info_dialog_type"),this.telegram.type,this.telegram.dpt||"",null!=this.telegram.payload?(0,r.qy)(f||(f=x`
                      <div class="detail-item payload">
                        <div class="detail-label">
                          ${0}
                        </div>
                        <code>${0}</code>
                      </div>
                    `),this.knx.localize("knx_telegram_info_dialog_payload"),this.telegram.payload):r.s6,this._previousTelegram,this.disablePrevious,v,this.hass.localize("ui.common.previous"),this._nextTelegram,this.disableNext,this.hass.localize("ui.common.next"),y)}_nextTelegram(){(0,n.r)(this,"next-telegram",void 0,{bubbles:!0})}_previousTelegram(){(0,n.r)(this,"previous-telegram",void 0,{bubbles:!0})}_handleKeyDown(e){if(this.telegram)switch(e.key){case"ArrowLeft":case"ArrowDown":this.disablePrevious||(e.preventDefault(),this._previousTelegram());break;case"ArrowRight":case"ArrowUp":this.disableNext||(e.preventDefault(),this._nextTelegram())}}static get styles(){return[a.nA,(0,r.AH)(b||(b=x`
        ha-dialog {
          --vertical-align-dialog: center;
          --dialog-z-index: 20;
        }
        @media all and (max-width: 450px), all and (max-height: 500px) {
          /* When in fullscreen dialog should be attached to top */
          ha-dialog {
            --dialog-surface-margin-top: 0px;
            --dialog-content-padding: 16px 24px 16px 24px;
          }
        }
        @media all and (min-width: 600px) and (min-height: 501px) {
          /* Set the dialog width and min-height, but let height adapt to content */
          ha-dialog {
            --mdc-dialog-min-width: 580px;
            --mdc-dialog-max-width: 580px;
            --mdc-dialog-min-height: 70%;
            --mdc-dialog-max-height: 100%;
            --dialog-content-padding: 16px 24px 16px 24px;
          }
        }

        ha-button {
          --ha-button-radius: 8px; /* Default is --wa-border-radius-pill */
        }

        /* Custom heading styles */
        .custom-heading {
          display: flex;
          flex-direction: row;
          padding: 16px 24px 12px 16px;
          border-bottom: 1px solid var(--divider-color);
          align-items: center;
          gap: 12px;
        }
        .heading-content {
          flex: 1;
          display: flex;
          flex-direction: column;
        }
        .header-title {
          margin: 0;
          font-size: 18px;
          font-weight: 500;
          line-height: 1.3;
          color: var(--primary-text-color);
        }
        .close-button {
          color: var(--primary-text-color);
          margin-right: -8px;
        }

        /* General content styling */
        .content {
          display: flex;
          flex-direction: column;
          flex: 1;
          gap: 16px;
          outline: none;
        }

        /* Timestamp style */
        .timestamp {
          font-size: 13px;
          color: var(--secondary-text-color);
          margin-top: 2px;
        }
        .direction-badge {
          font-size: 12px;
          font-weight: 500;
          padding: 3px 10px;
          border-radius: 12px;
          text-transform: uppercase;
          letter-spacing: 0.4px;
          white-space: nowrap;
        }
        .direction-badge.outgoing {
          background-color: var(--knx-blue, var(--info-color));
          color: var(--text-primary-color, #fff);
        }
        .direction-badge.incoming {
          background-color: var(--knx-green, var(--success-color));
          color: var(--text-primary-color, #fff);
        }

        /* Body: addresses + value + details */
        .telegram-body {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .addresses-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
        }
        @media (max-width: 450px) {
          .addresses-row {
            grid-template-columns: 1fr;
            gap: 12px;
          }
        }
        .address-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
          background: var(--card-background-color);
          padding: 0px 12px 0px 12px;
          border-radius: 8px;
        }
        .item-label {
          font-size: 13px;
          font-weight: 500;
          color: var(--secondary-text-color);
          margin-bottom: 4px;
          letter-spacing: 0.5px;
        }
        .address-chip {
          font-family: var(--code-font-family, monospace);
          font-size: 16px;
          font-weight: 500;
          background: var(--secondary-background-color);
          border-radius: 12px;
          padding: 6px 12px;
          text-align: center;
          box-shadow: 0 1px 2px rgba(var(--rgb-primary-text-color), 0.06);
        }
        .item-name {
          font-size: 12px;
          color: var(--secondary-text-color);
          font-style: italic;
          margin-top: 4px;
          text-align: center;
        }

        /* Value section */
        .value-section {
          padding: 16px;
          background: var(--primary-background-color);
          border-radius: 8px;
          box-shadow: 0 1px 2px rgba(var(--rgb-primary-text-color), 0.06);
        }
        .value-label {
          font-size: 13px;
          color: var(--secondary-text-color);
          margin-bottom: 8px;
          font-weight: 500;
          letter-spacing: 0.4px;
        }
        .value-content {
          font-family: var(--code-font-family, monospace);
          font-size: 22px;
          font-weight: 600;
          color: var(--primary-color);
          text-align: center;
        }

        /* Telegram details (type/DPT/payload) */
        .telegram-details {
          padding: 16px;
          background: var(--secondary-background-color);
          border-radius: 8px;
          box-shadow: 0 1px 2px rgba(var(--rgb-primary-text-color), 0.06);
        }
        .detail-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
        }
        .detail-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .detail-item.payload {
          grid-column: span 2;
          margin-top: 4px;
        }
        .detail-label {
          font-size: 13px;
          color: var(--secondary-text-color);
          font-weight: 500;
        }
        .detail-value {
          font-size: 14px;
          font-weight: 500;
        }
        code {
          font-family: var(--code-font-family, monospace);
          font-size: 13px;
          background: var(--card-background-color);
          padding: 8px 12px;
          border-radius: 6px;
          display: block;
          overflow-x: auto;
          white-space: pre;
          box-shadow: 0 1px 2px rgba(var(--rgb-primary-text-color), 0.04);
          margin-top: 4px;
        }

        .primaryAction {
          margin-right: 8px;
        }
      `))]}constructor(...e){super(...e),this.narrow=!1,this.disableNext=!1,this.disablePrevious=!1}}(0,o.__decorate)([(0,s.MZ)({attribute:!1})],$.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],$.prototype,"knx",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],$.prototype,"narrow",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],$.prototype,"telegram",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],$.prototype,"disableNext",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],$.prototype,"disablePrevious",void 0),$=(0,o.__decorate)([(0,s.EM)("knx-group-monitor-telegram-info-dialog")],$),t()}catch(p){t(p)}}))},27513:function(e,t,i){i.a(e,(async function(e,o){try{i.r(t),i.d(t,{KNXGroupMonitor:function(){return V}});i(79827),i(35748),i(65315),i(837),i(59023),i(5934),i(47849),i(18223),i(95013);var r=i(69868),s=i(84922),n=i(65940),a=i(92491),l=i(55204),d=(i(23749),i(76943)),c=(i(93672),i(28210)),h=i(17229),p=(i(62754),i(8725),i(31123)),u=(i(36876),i(11991)),g=i(93060),m=i(62620),_=e([a,l,d,p]);[a,l,d,p]=_.then?(await _)():_;let f,b,x,v,y,k,$,w,C,F,T,D,M,S,z,A=e=>e;const L="M15,16H19V18H15V16M15,8H22V10H15V8M15,12H21V14H15V12M3,18A2,2 0 0,0 5,20H11A2,2 0 0,0 13,18V8H3V18M14,5H11L10,4H6L5,5H2V7H14V5Z",I="M13,6V18L21.5,12M4,18L12.5,12L4,6V18Z",H="M14,19H18V5H14M6,19H10V5H6V19Z",E="M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z";class V extends s.WF{static get styles(){return[(0,s.AH)(f||(f=A`
        :host {
          --table-row-alternative-background-color: var(--primary-background-color);
        }

        ha-icon-button.active {
          color: var(--primary-color);
        }

        .table-header {
          border-bottom: 1px solid var(--divider-color);
          padding-bottom: 12px;
        }

        :host {
          --ha-data-table-row-style: {
            font-size: 0.9em;
            padding: 8px 0;
          };
        }

        .filter-wrapper {
          display: flex;
          flex-direction: column;
        }

        .toolbar-actions {
          padding-left: 8px;
          display: flex;
          align-items: center;
          gap: 8px;
        }
      `))]}get isMobileTouchDevice(){return c.M&&h.C}_getFilteredData(){return this.controller.getFilteredTelegramsAndDistinctValues()}async firstUpdated(){await this.controller.setup(this.hass)}get searchLabel(){if(this.narrow)return this.knx.localize("group_monitor_search_label_narrow");const{filteredTelegrams:e}=this._getFilteredData(),t=e.length,i=1===t?"group_monitor_search_label_singular":"group_monitor_search_label";return this.knx.localize(i,{count:t})}_hasActiveFilters(e){if(e){const t=this.controller.filters[e];return Array.isArray(t)&&t.length>0}return Object.values(this.controller.filters).some((e=>Array.isArray(e)&&e.length>0))}_handleSortingChanged({detail:{column:e,direction:t}}){this.controller.sortColumn=t?e:void 0,this.controller.sortDirection=t||void 0}_handleRowClick(e){this.controller.selectedTelegramId=e.detail.id}_handleDialogClosed(){this.controller.selectedTelegramId=null}async _handlePauseToggle(){await this.controller.togglePause()}async _handleReload(){await this.controller.reload(this.hass)}async _retryConnection(){await this.controller.retryConnection(this.hass)}_handleClearFilters(){this.controller.clearFilters(this.route)}_handleClearRows(){this.controller.clearTelegrams()}_selectNextTelegram(){const{filteredTelegrams:e}=this._getFilteredData();this.controller.navigateTelegram(1,e)}_selectPreviousTelegram(){const{filteredTelegrams:e}=this._getFilteredData();this.controller.navigateTelegram(-1,e)}_formatOffsetWithPrecision(e){if(null===e)return(0,g.RL)(e);return 0===Math.round(e/1e3)&&0!==e?(0,g.RL)(e,"microseconds"):(0,g.RL)(e,"milliseconds")}_renderTelegramInfoDialog(e){const{filteredTelegrams:t}=this._getFilteredData(),i=t.findIndex((t=>t.id===e)),o=t[i];return o?(0,s.qy)(b||(b=A`
      <knx-group-monitor-telegram-info-dialog
        .hass=${0}
        .knx=${0}
        .narrow=${0}
        .telegram=${0}
        .disableNext=${0}
        .disablePrevious=${0}
        @next-telegram=${0}
        @previous-telegram=${0}
        @dialog-closed=${0}
      >
      </knx-group-monitor-telegram-info-dialog>
    `),this.hass,this.knx,this.narrow,o,i+1>=t.length,i<=0,this._selectNextTelegram,this._selectPreviousTelegram,this._handleDialogClosed):s.s6}render(){var e,t,i,o;const r=Object.values(this.controller.filters).filter((e=>Array.isArray(e)&&e.length)).length,{filteredTelegrams:n,distinctValues:a}=this._getFilteredData();return(0,s.qy)(x||(x=A`
      <hass-tabs-subpage-data-table
        .hass=${0}
        .narrow=${0}
        .route=${0}
        .tabs=${0}
        .columns=${0}
        .noDataText=${0}
        .data=${0}
        .hasFab=${0}
        .searchLabel=${0}
        .localizeFunc=${0}
        id="id"
        .clickable=${0}
        .initialSorting=${0}
        @row-click=${0}
        @sorting-changed=${0}
        has-filters
        .filters=${0}
        @clear-filter=${0}
      >
        <!-- Top header -->
        ${0}
        ${0}
        ${0}

        <!-- Toolbar actions -->
        <div slot="toolbar-icon" class="toolbar-actions">
          <ha-icon-button
            .label=${0}
            .path=${0}
            class=${0}
            @click=${0}
            data-testid="pause-button"
            .title=${0}
          >
          </ha-icon-button>
          <ha-icon-button
            .label=${0}
            .path=${0}
            @click=${0}
            ?disabled=${0}
            data-testid="clean-button"
            .title=${0}
          >
          </ha-icon-button>
          <ha-icon-button
            .label=${0}
            .path=${0}
            @click=${0}
            ?disabled=${0}
            data-testid="reload-button"
            .title=${0}
          >
          </ha-icon-button>
        </div>

        <!-- Filter for Source Address -->
        <knx-list-filter
          data-filter="source"
          slot="filter-pane"
          .hass=${0}
          .knx=${0}
          .data=${0}
          .config=${0}
          .selectedOptions=${0}
          .expanded=${0}
          .narrow=${0}
          .isMobileDevice=${0}
          .filterTitle=${0}
          @selection-changed=${0}
          @expanded-changed=${0}
          @sort-changed=${0}
        ></knx-list-filter>

        <!-- Filter for Destination Address -->
        <knx-list-filter
          data-filter="destination"
          slot="filter-pane"
          .hass=${0}
          .knx=${0}
          .data=${0}
          .config=${0}
          .selectedOptions=${0}
          .expanded=${0}
          .narrow=${0}
          .isMobileDevice=${0}
          .filterTitle=${0}
          @selection-changed=${0}
          @expanded-changed=${0}
          @sort-changed=${0}
        ></knx-list-filter>

        <!-- Filter for Direction -->
        <knx-list-filter
          slot="filter-pane"
          .hass=${0}
          .knx=${0}
          .data=${0}
          .config=${0}
          .selectedOptions=${0}
          .pinSelectedItems=${0}
          .expanded=${0}
          .narrow=${0}
          .isMobileDevice=${0}
          .filterTitle=${0}
          @selection-changed=${0}
          @expanded-changed=${0}
        ></knx-list-filter>

        <!-- Filter for Telegram Type -->
        <knx-list-filter
          slot="filter-pane"
          .hass=${0}
          .knx=${0}
          .data=${0}
          .config=${0}
          .selectedOptions=${0}
          .pinSelectedItems=${0}
          .expanded=${0}
          .narrow=${0}
          .isMobileDevice=${0}
          .filterTitle=${0}
          @selection-changed=${0}
          @expanded-changed=${0}
        ></knx-list-filter>
      </hass-tabs-subpage-data-table>

      <!-- Telegram detail dialog -->
      ${0}
    `),this.hass,this.narrow,this.route,this.tabs,this._columns(this.narrow,!0===this.controller.isProjectLoaded,this.hass.language),this.knx.localize("group_monitor_waiting_message"),n,!1,this.searchLabel,this.knx.localize,!0,{column:this.controller.sortColumn||"timestampIso",direction:this.controller.sortDirection||"desc"},this._handleRowClick,this._handleSortingChanged,r,this._handleClearFilters,this.controller.connectionError?(0,s.qy)(v||(v=A`
              <ha-alert
                slot="top-header"
                .alertType=${0}
                .title=${0}
              >
                ${0}
                <ha-button slot="action" @click=${0}>
                  ${0}
                </ha-button>
              </ha-alert>
            `),"error",this.knx.localize("group_monitor_connection_error_title"),this.controller.connectionError,this._retryConnection,this.knx.localize("group_monitor_retry_connection")):s.s6,this.controller.isPaused?(0,s.qy)(y||(y=A`
              <ha-alert
                slot="top-header"
                .alertType=${0}
                .dismissable=${0}
                .title=${0}
              >
                ${0}
                <ha-button slot="action" @click=${0}>
                  ${0}
                </ha-button>
              </ha-alert>
            `),"info",!1,this.knx.localize("group_monitor_paused_title"),this.knx.localize("group_monitor_paused_message"),this._handlePauseToggle,this.knx.localize("group_monitor_resume")):"",!1===this.controller.isProjectLoaded?(0,s.qy)(k||(k=A`
              <ha-alert
                slot="top-header"
                .alertType=${0}
                .dismissable=${0}
                .title=${0}
              >
                ${0}
              </ha-alert>
            `),"info",!0,this.knx.localize("group_monitor_project_not_loaded_title"),this.knx.localize("group_monitor_project_not_loaded_message")):s.s6,this.controller.isPaused?this.knx.localize("group_monitor_resume"):this.knx.localize("group_monitor_pause"),this.controller.isPaused?I:H,this.controller.isPaused?"active":"",this._handlePauseToggle,this.controller.isPaused?this.knx.localize("group_monitor_resume"):this.knx.localize("group_monitor_pause"),this.knx.localize("group_monitor_clear"),L,this._handleClearRows,0===this.controller.telegrams.length,this.knx.localize("group_monitor_clear"),this.knx.localize("group_monitor_reload"),E,this._handleReload,!this.controller.isReloadEnabled,this.knx.localize("group_monitor_reload"),this.hass,this.knx,Object.values(a.source),this._sourceFilterConfig(this._hasActiveFilters("source"),(null===(e=this.controller.filters.source)||void 0===e?void 0:e.length)||0,null===(t=this.sourceFilter)||void 0===t?void 0:t.sortCriterion,this.hass.language),this.controller.filters.source,"source"===this.controller.expandedFilter,this.narrow,this.isMobileTouchDevice,this.knx.localize("group_monitor_source"),this._handleSourceFilterChange,this._handleSourceFilterExpanded,this._handleFilterSortChanged,this.hass,this.knx,Object.values(a.destination),this._destinationFilterConfig(this._hasActiveFilters("destination"),(null===(i=this.controller.filters.destination)||void 0===i?void 0:i.length)||0,null===(o=this.destinationFilter)||void 0===o?void 0:o.sortCriterion,this.hass.language),this.controller.filters.destination,"destination"===this.controller.expandedFilter,this.narrow,this.isMobileTouchDevice,this.knx.localize("group_monitor_destination"),this._handleDestinationFilterChange,this._handleDestinationFilterExpanded,this._handleFilterSortChanged,this.hass,this.knx,Object.values(a.direction),this._directionFilterConfig(this._hasActiveFilters("direction"),this.hass.language),this.controller.filters.direction,!1,"direction"===this.controller.expandedFilter,this.narrow,this.isMobileTouchDevice,this.knx.localize("group_monitor_direction"),this._handleDirectionFilterChange,this._handleDirectionFilterExpanded,this.hass,this.knx,Object.values(a.telegramtype),this._telegramTypeFilterConfig(this._hasActiveFilters("telegramtype"),this.hass.language),this.controller.filters.telegramtype,!1,"telegramtype"===this.controller.expandedFilter,this.narrow,this.isMobileTouchDevice,this.knx.localize("group_monitor_type"),this._handleTelegramTypeFilterChange,this._handleTelegramTypeFilterExpanded,null!==this.controller.selectedTelegramId?this._renderTelegramInfoDialog(this.controller.selectedTelegramId):s.s6)}constructor(...e){super(...e),this.controller=new m.K(this),this._sourceFilterConfig=(0,n.A)(((e,t,i,o)=>({idField:{filterable:!1,sortable:!1,mapper:e=>e.id},primaryField:{fieldName:this.knx.localize("telegram_filter_source_sort_by_primaryText"),filterable:!0,sortable:!0,sortAscendingText:this.knx.localize("telegram_filter_sort_ascending"),sortDescendingText:this.knx.localize("telegram_filter_sort_descending"),sortDefaultDirection:"asc",mapper:e=>e.id},secondaryField:{fieldName:this.knx.localize("telegram_filter_source_sort_by_secondaryText"),filterable:!0,sortable:!0,sortAscendingText:this.knx.localize("telegram_filter_sort_ascending"),sortDescendingText:this.knx.localize("telegram_filter_sort_descending"),sortDefaultDirection:"asc",mapper:e=>e.name},badgeField:{fieldName:this.knx.localize("telegram_filter_source_sort_by_badge"),filterable:!1,sortable:!1,mapper:t=>e?`${t.filteredCount}/${t.totalCount}`:`${t.totalCount}`},custom:{totalCount:{fieldName:this.knx.localize("telegram_filter_sort_by_total_count"),filterable:!1,sortable:!0,sortAscendingText:this.knx.localize("telegram_filter_sort_ascending"),sortDescendingText:this.knx.localize("telegram_filter_sort_descending"),sortDefaultDirection:"desc",mapper:e=>e.totalCount.toString()},filteredCount:{fieldName:this.knx.localize("telegram_filter_sort_by_filtered_count"),filterable:!1,sortable:t>0||"filteredCount"===i,sortDisabled:0===t,sortAscendingText:this.knx.localize("telegram_filter_sort_ascending"),sortDescendingText:this.knx.localize("telegram_filter_sort_descending"),sortDefaultDirection:"desc",mapper:e=>(e.filteredCount||0).toString()}}}))),this._destinationFilterConfig=(0,n.A)(((e,t,i,o)=>({idField:{filterable:!1,sortable:!1,mapper:e=>e.id},primaryField:{fieldName:this.knx.localize("telegram_filter_destination_sort_by_primaryText"),filterable:!0,sortable:!0,sortAscendingText:this.knx.localize("telegram_filter_sort_ascending"),sortDescendingText:this.knx.localize("telegram_filter_sort_descending"),sortDefaultDirection:"asc",mapper:e=>e.id},secondaryField:{fieldName:this.knx.localize("telegram_filter_destination_sort_by_secondaryText"),filterable:!0,sortable:!0,sortAscendingText:this.knx.localize("telegram_filter_sort_ascending"),sortDescendingText:this.knx.localize("telegram_filter_sort_descending"),sortDefaultDirection:"asc",mapper:e=>e.name},badgeField:{fieldName:this.knx.localize("telegram_filter_destination_sort_by_badge"),filterable:!1,sortable:!1,mapper:t=>e?`${t.filteredCount}/${t.totalCount}`:`${t.totalCount}`},custom:{totalCount:{fieldName:this.knx.localize("telegram_filter_sort_by_total_count"),filterable:!1,sortable:!0,sortAscendingText:this.knx.localize("telegram_filter_sort_ascending"),sortDescendingText:this.knx.localize("telegram_filter_sort_descending"),sortDefaultDirection:"desc",mapper:e=>e.totalCount.toString()},filteredCount:{fieldName:this.knx.localize("telegram_filter_sort_by_filtered_count"),filterable:!1,sortable:t>0||"filteredCount"===i,sortDisabled:0===t,sortAscendingText:this.knx.localize("telegram_filter_sort_ascending"),sortDescendingText:this.knx.localize("telegram_filter_sort_descending"),sortDefaultDirection:"desc",mapper:e=>(e.filteredCount||0).toString()}}}))),this._directionFilterConfig=(0,n.A)(((e,t)=>({idField:{filterable:!1,sortable:!1,mapper:e=>e.id},primaryField:{filterable:!1,sortable:!1,mapper:e=>e.id},secondaryField:{filterable:!1,sortable:!1,mapper:e=>e.name},badgeField:{filterable:!1,sortable:!1,mapper:t=>e?`${t.filteredCount}/${t.totalCount}`:`${t.totalCount}`}}))),this._telegramTypeFilterConfig=(0,n.A)(((e,t)=>({idField:{filterable:!1,sortable:!1,mapper:e=>e.id},primaryField:{filterable:!1,sortable:!1,mapper:e=>e.id},secondaryField:{filterable:!1,sortable:!1,mapper:e=>e.name},badgeField:{filterable:!1,sortable:!1,mapper:t=>e?`${t.filteredCount}/${t.totalCount}`:`${t.totalCount}`}}))),this._onFilterSelectionChange=(e,t)=>{this.controller.setFilterFieldValue(e,t,this.route)},this._onFilterExpansionChange=(e,t)=>{this.controller.updateExpandedFilter(e,t)},this._handleSourceFilterChange=e=>{this._onFilterSelectionChange("source",e.detail.value)},this._handleSourceFilterExpanded=e=>{this._onFilterExpansionChange("source",e.detail.expanded)},this._handleDestinationFilterChange=e=>{this._onFilterSelectionChange("destination",e.detail.value)},this._handleDestinationFilterExpanded=e=>{this._onFilterExpansionChange("destination",e.detail.expanded)},this._handleDirectionFilterChange=e=>{this._onFilterSelectionChange("direction",e.detail.value)},this._handleDirectionFilterExpanded=e=>{this._onFilterExpansionChange("direction",e.detail.expanded)},this._handleTelegramTypeFilterChange=e=>{this._onFilterSelectionChange("telegramtype",e.detail.value)},this._handleTelegramTypeFilterExpanded=e=>{this._onFilterExpansionChange("telegramtype",e.detail.expanded)},this._handleSourceFilterToggle=e=>{this.controller.toggleFilterValue("source",e.detail.value,this.route)},this._handleDestinationFilterToggle=e=>{this.controller.toggleFilterValue("destination",e.detail.value,this.route)},this._handleTelegramTypeFilterToggle=e=>{this.controller.toggleFilterValue("telegramtype",e.detail.value,this.route)},this._handleFilterSortChanged=e=>{this.requestUpdate()},this._columns=(0,n.A)(((e,t,i)=>({timestampIso:{showNarrow:!1,filterable:!0,sortable:!0,direction:"desc",title:this.knx.localize("group_monitor_time"),minWidth:"110px",maxWidth:"122px",template:e=>(0,s.qy)($||($=A`
          <knx-table-cell>
            <div class="primary" slot="primary">${0}</div>
            ${0}
          </knx-table-cell>
        `),(0,g.Zc)(e.timestamp),null===e.offset||"timestampIso"!==this.controller.sortColumn&&void 0!==this.controller.sortColumn?s.s6:(0,s.qy)(w||(w=A`
                  <div class="secondary" slot="secondary">
                    <span>+</span>
                    <span>${0}</span>
                  </div>
                `),this._formatOffsetWithPrecision(e.offset)))},sourceAddress:{showNarrow:!0,filterable:!0,sortable:!0,title:this.knx.localize("group_monitor_source"),flex:2,minWidth:"0",template:e=>(0,s.qy)(C||(C=A`
          <knx-table-cell-filterable
            .knx=${0}
            .filterValue=${0}
            .filterDisplayText=${0}
            .filterActive=${0}
            .filterDisabled=${0}
            @toggle-filter=${0}
          >
            <div class="primary" slot="primary">${0}</div>
            ${0}
          </knx-table-cell-filterable>
        `),this.knx,e.sourceAddress,e.sourceAddress,(this.controller.filters.source||[]).includes(e.sourceAddress),this.isMobileTouchDevice,this._handleSourceFilterToggle,e.sourceAddress,e.sourceText?(0,s.qy)(F||(F=A`
                  <div class="secondary" slot="secondary" title=${0}>
                    ${0}
                  </div>
                `),e.sourceText||"",e.sourceText):s.s6)},sourceText:{hidden:!0,filterable:!0,sortable:!0,title:this.knx.localize("group_monitor_source_name")},sourceName:{showNarrow:!0,hidden:!0,sortable:!1,groupable:!0,filterable:!1,title:this.knx.localize("group_monitor_source")},destinationAddress:{showNarrow:!0,sortable:!0,filterable:!0,title:this.knx.localize("group_monitor_destination"),flex:2,minWidth:"0",template:e=>(0,s.qy)(T||(T=A`
          <knx-table-cell-filterable
            .knx=${0}
            .filterValue=${0}
            .filterDisplayText=${0}
            .filterActive=${0}
            .filterDisabled=${0}
            @toggle-filter=${0}
          >
            <div class="primary" slot="primary">${0}</div>
            ${0}
          </knx-table-cell-filterable>
        `),this.knx,e.destinationAddress,e.destinationAddress,(this.controller.filters.destination||[]).includes(e.destinationAddress),this.isMobileTouchDevice,this._handleDestinationFilterToggle,e.destinationAddress,e.destinationText?(0,s.qy)(D||(D=A`
                  <div class="secondary" slot="secondary" title=${0}>
                    ${0}
                  </div>
                `),e.destinationText||"",e.destinationText):s.s6)},destinationText:{showNarrow:!0,hidden:!0,sortable:!0,filterable:!0,title:this.knx.localize("group_monitor_destination_name")},destinationName:{showNarrow:!0,hidden:!0,sortable:!1,groupable:!0,filterable:!1,title:this.knx.localize("group_monitor_destination")},type:{showNarrow:!1,title:this.knx.localize("group_monitor_type"),filterable:!0,sortable:!0,groupable:!0,minWidth:"155px",maxWidth:"155px",template:e=>(0,s.qy)(M||(M=A`
          <knx-table-cell-filterable
            .knx=${0}
            .filterValue=${0}
            .filterDisplayText=${0}
            .filterActive=${0}
            .filterDisabled=${0}
            @toggle-filter=${0}
          >
            <div class="primary" slot="primary" title=${0}>${0}</div>
            <div
              class="secondary"
              slot="secondary"
              style="color: ${0}"
            >
              ${0}
            </div>
          </knx-table-cell-filterable>
        `),this.knx,e.type,e.type,(this.controller.filters.telegramtype||[]).includes(e.type),this.isMobileTouchDevice,this._handleTelegramTypeFilterToggle,e.type,e.type,"Outgoing"===e.direction?"var(--knx-blue)":"var(--knx-green)",e.direction)},direction:{hidden:!0,title:this.knx.localize("group_monitor_direction"),filterable:!0,groupable:!0},payload:{showNarrow:!1,hidden:e&&t,title:this.knx.localize("group_monitor_payload"),filterable:!0,sortable:!0,type:"numeric",minWidth:"105px",maxWidth:"105px",template:e=>e.payload?(0,s.qy)(S||(S=A`
            <code
              style="
                display: inline-block;
                box-sizing: border-box;
                max-width: 100%;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                font-size: 0.9em;
                background: var(--secondary-background-color);
                padding: 2px 4px;
                border-radius: 4px;
              "
              title=${0}
            >
              ${0}
            </code>
          `),e.payload,e.payload):s.s6},value:{showNarrow:!0,hidden:!t,title:this.knx.localize("group_monitor_value"),filterable:!0,sortable:!0,flex:1,minWidth:"0",template:e=>{const t=e.value;return t?(0,s.qy)(z||(z=A`
            <knx-table-cell>
              <span
                class="primary"
                slot="primary"
                style="font-weight: 500; color: var(--primary-color);"
                title=${0}
              >
                ${0}
              </span>
            </knx-table-cell>
          `),t,t):s.s6}}})))}}(0,r.__decorate)([(0,u.MZ)({type:Object})],V.prototype,"hass",void 0),(0,r.__decorate)([(0,u.MZ)({attribute:!1})],V.prototype,"knx",void 0),(0,r.__decorate)([(0,u.MZ)({type:Boolean,reflect:!0})],V.prototype,"narrow",void 0),(0,r.__decorate)([(0,u.MZ)({type:Object})],V.prototype,"route",void 0),(0,r.__decorate)([(0,u.MZ)({type:Array,reflect:!1})],V.prototype,"tabs",void 0),(0,r.__decorate)([(0,u.P)('knx-list-filter[data-filter="source"]')],V.prototype,"sourceFilter",void 0),(0,r.__decorate)([(0,u.P)('knx-list-filter[data-filter="destination"]')],V.prototype,"destinationFilter",void 0),V=(0,r.__decorate)([(0,u.EM)("knx-group-monitor")],V),o()}catch(f){o(f)}}))},22103:function(e,t,i){i.d(t,{H:function(){return n}});i(91455),i(62928),i(42124),i(86581),i(67579),i(41190),i(47849),i(1485),i(30500),i(91844);var o=i(27554),r=i(67874),s=i(19490);function n(e,t){var i;const n=()=>(0,r.w)(null==t?void 0:t.in,NaN),m=null!==(i=null==t?void 0:t.additionalDigits)&&void 0!==i?i:2,_=function(e){const t={},i=e.split(a.dateTimeDelimiter);let o;if(i.length>2)return t;/:/.test(i[0])?o=i[0]:(t.date=i[0],o=i[1],a.timeZoneDelimiter.test(t.date)&&(t.date=e.split(a.timeZoneDelimiter)[0],o=e.substr(t.date.length,e.length)));if(o){const e=a.timezone.exec(o);e?(t.time=o.replace(e[1],""),t.timezone=e[1]):t.time=o}return t}(e);let f;if(_.date){const e=function(e,t){const i=new RegExp("^(?:(\\d{4}|[+-]\\d{"+(4+t)+"})|(\\d{2}|[+-]\\d{"+(2+t)+"})$)"),o=e.match(i);if(!o)return{year:NaN,restDateString:""};const r=o[1]?parseInt(o[1]):null,s=o[2]?parseInt(o[2]):null;return{year:null===s?r:100*s,restDateString:e.slice((o[1]||o[2]).length)}}(_.date,m);f=function(e,t){if(null===t)return new Date(NaN);const i=e.match(l);if(!i)return new Date(NaN);const o=!!i[4],r=h(i[1]),s=h(i[2])-1,n=h(i[3]),a=h(i[4]),d=h(i[5])-1;if(o)return function(e,t,i){return t>=1&&t<=53&&i>=0&&i<=6}(0,a,d)?function(e,t,i){const o=new Date(0);o.setUTCFullYear(e,0,4);const r=o.getUTCDay()||7,s=7*(t-1)+i+1-r;return o.setUTCDate(o.getUTCDate()+s),o}(t,a,d):new Date(NaN);{const e=new Date(0);return function(e,t,i){return t>=0&&t<=11&&i>=1&&i<=(u[t]||(g(e)?29:28))}(t,s,n)&&function(e,t){return t>=1&&t<=(g(e)?366:365)}(t,r)?(e.setUTCFullYear(t,s,Math.max(r,n)),e):new Date(NaN)}}(e.restDateString,e.year)}if(!f||isNaN(+f))return n();const b=+f;let x,v=0;if(_.time&&(v=function(e){const t=e.match(d);if(!t)return NaN;const i=p(t[1]),r=p(t[2]),s=p(t[3]);if(!function(e,t,i){if(24===e)return 0===t&&0===i;return i>=0&&i<60&&t>=0&&t<60&&e>=0&&e<25}(i,r,s))return NaN;return i*o.s0+r*o.Cg+1e3*s}(_.time),isNaN(v)))return n();if(!_.timezone){const e=new Date(b+v),i=(0,s.a)(0,null==t?void 0:t.in);return i.setFullYear(e.getUTCFullYear(),e.getUTCMonth(),e.getUTCDate()),i.setHours(e.getUTCHours(),e.getUTCMinutes(),e.getUTCSeconds(),e.getUTCMilliseconds()),i}return x=function(e){if("Z"===e)return 0;const t=e.match(c);if(!t)return 0;const i="+"===t[1]?-1:1,r=parseInt(t[2]),s=t[3]&&parseInt(t[3])||0;if(!function(e,t){return t>=0&&t<=59}(0,s))return NaN;return i*(r*o.s0+s*o.Cg)}(_.timezone),isNaN(x)?n():(0,s.a)(b+v+x,null==t?void 0:t.in)}const a={dateTimeDelimiter:/[T ]/,timeZoneDelimiter:/[Z ]/i,timezone:/([Z+-].*)$/},l=/^-?(?:(\d{3})|(\d{2})(?:-?(\d{2}))?|W(\d{2})(?:-?(\d{1}))?|)$/,d=/^(\d{2}(?:[.,]\d*)?)(?::?(\d{2}(?:[.,]\d*)?))?(?::?(\d{2}(?:[.,]\d*)?))?$/,c=/^([+-])(\d{2})(?::?(\d{2}))?$/;function h(e){return e?parseInt(e):1}function p(e){return e&&parseFloat(e.replace(",","."))||0}const u=[31,null,31,30,31,30,31,31,30,31,30,31];function g(e){return e%400==0||e%4==0&&e%100!=0}},17747:function(e,t,i){i.d(t,{a:function(){return n}});i(35748),i(65315),i(12840),i(95013);var o=i(11681),r=i(64363);const s={},n=(0,r.u$)(class extends r.WL{render(e,t){return t()}update(e,[t,i]){if(Array.isArray(t)){if(Array.isArray(this.ot)&&this.ot.length===t.length&&t.every(((e,t)=>e===this.ot[t])))return o.c0}else if(this.ot===t)return o.c0;return this.ot=Array.isArray(t)?Array.from(t):t,this.render(t,i)}constructor(){super(...arguments),this.ot=s}})}}]);
//# sourceMappingURL=50.7c7bc2c8bca8a2e2.js.map