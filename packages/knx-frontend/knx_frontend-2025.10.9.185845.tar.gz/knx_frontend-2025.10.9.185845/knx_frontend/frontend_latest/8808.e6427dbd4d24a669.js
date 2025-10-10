export const __webpack_id__="8808";export const __webpack_ids__=["8808"];export const __webpack_modules__={87835:function(e,o,t){t.r(o),t.d(o,{HaBooleanSelector:()=>l});var a=t(69868),r=t(84922),d=t(11991),i=t(73120);t(52893),t(43143),t(20014);class l extends r.WF{render(){return r.qy`
      <ha-formfield alignEnd spaceBetween .label=${this.label}>
        <ha-switch
          .checked=${this.value??!0===this.placeholder}
          @change=${this._handleChange}
          .disabled=${this.disabled}
        ></ha-switch>
        <span slot="label">
          <p class="primary">${this.label}</p>
          ${this.helper?r.qy`<p class="secondary">${this.helper}</p>`:r.s6}
        </span>
      </ha-formfield>
    `}_handleChange(e){const o=e.target.checked;this.value!==o&&(0,i.r)(this,"value-changed",{value:o})}constructor(...e){super(...e),this.value=!1,this.disabled=!1}}l.styles=r.AH`
    ha-formfield {
      display: flex;
      min-height: 56px;
      align-items: center;
      --mdc-typography-body2-font-size: 1em;
    }
    p {
      margin: 0;
    }
    .secondary {
      direction: var(--direction);
      padding-top: 4px;
      box-sizing: border-box;
      color: var(--secondary-text-color);
      font-size: 0.875rem;
      font-weight: var(
        --mdc-typography-body2-font-weight,
        var(--ha-font-weight-normal)
      );
    }
  `,(0,a.__decorate)([(0,d.MZ)({attribute:!1})],l.prototype,"hass",void 0),(0,a.__decorate)([(0,d.MZ)({type:Boolean})],l.prototype,"value",void 0),(0,a.__decorate)([(0,d.MZ)()],l.prototype,"placeholder",void 0),(0,a.__decorate)([(0,d.MZ)()],l.prototype,"label",void 0),(0,a.__decorate)([(0,d.MZ)()],l.prototype,"helper",void 0),(0,a.__decorate)([(0,d.MZ)({type:Boolean})],l.prototype,"disabled",void 0),l=(0,a.__decorate)([(0,d.EM)("ha-selector-boolean")],l)}};
//# sourceMappingURL=8808.e6427dbd4d24a669.js.map