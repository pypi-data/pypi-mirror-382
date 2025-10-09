<script lang="ts">
  import type { Gradio } from "@gradio/utils";
  import { Block } from "@gradio/atoms";
  import { StatusTracker } from "@gradio/statustracker";
  import type { LoadingStatus } from "@gradio/statustracker";
  import ScrollEffect from "./shared/ScrollEffect.svelte";
  import StarWarsEffect from "./shared/StarWarsEffect.svelte";
  import MatrixEffect from "./shared/MatrixEffect.svelte";
  import { Image } from "@gradio/image/shared";

  /**
   * Props for the Index component.
   * @typedef {Object} Value
   * @property {Array<{title?: string, name?: string, section_title?: string}>} credits - List of credits with title and name.
   * @property {Record<string, string>} licenses - License names and content.
   * @property {"scroll" | "starwars" | "matrix"} effect - Credits display effect.
   * @property {number} speed - Animation speed in seconds.
   * @property {number} base_font_size - Base font size in rem.
   * @property {string | null} intro_title - Intro title.
   * @property {string | null} intro_subtitle - Intro subtitle.
   * @property {"right" | "bottom"} sidebar_position - Licenses sidebar position.
   * @property {{path: string | null, url: string | null, orig_name: string | null, mime_type: string | null} | null} logo_path - Logo file details.
   * @property {boolean} show_logo - Show logo.
   * @property {boolean} show_licenses - Show licenses.
   * @property {boolean} show_credits - Show credits.
   * @property {"center" | "left" | "right"} logo_position - Logo alignment.
   * @property {"stretch" | "crop" | "resize"} logo_sizing - Logo sizing mode.
   * @property {number | string | null} logo_width - Logo width.
   * @property {number | string | null} logo_height - Logo height.
   * @property {string | null} scroll_background_color - Scroll effect background color.
   * @property {string | null} scroll_title_color - Credit title color.
   * @property {string | null} scroll_section_title_color - Section title color.
   * @property {string | null} scroll_name_color - Credit name color.
   * @property {number} title_font_size - Title font size (unused in StarWarsEffect).
   * @property {number} name_font_size - Name font size (unused in StarWarsEffect).
   * @property {"stacked" | "two-column"} layout_style - Credit layout style.
   * @property {boolean} title_uppercase - Transform title to uppercase.
   * @property {boolean} name_uppercase - Transform name to uppercase.
   * @property {boolean} section_title_uppercase - Transform section title to uppercase.
   * @property {boolean} swap_font_sizes_on_two_column - Swap title/name font sizes in two-column layout.
   * @property {{path: string | null, url: string | null, ...} | null} scroll_logo_path - Logo to display inside the scroll.
   * @property {string} scroll_logo_height - Height of the scrolling logo.
   */
  export let value: Value | null = null;
  export let elem_id = "";
  export let elem_classes: string[] = [];
  export let visible = true;
  export let container = true;
  export let scale: number | null = null;
  export let min_width: number | undefined = undefined;
  export let height: number | string | undefined = undefined;
  export let width: number | string | undefined = undefined;
  export let loading_status: LoadingStatus;
  export let gradio: Gradio<{ change: never }>;

  // Default value if `value` is null
  $: effectiveValue = value || {
    credits: [
      { section_title: "Default Team"},
      { title: "Lead Developer", name: "John Doe" },
      { title: "UI/UX Design", name: "Jane Smith" },
    ],
    licenses: {
      "Gradio Framework": "Apache License placeholder",
      "This Component": "MIT License placeholder",
    },
    effect: "scroll",
    speed: 40,
    base_font_size: 1.5,
    intro_title: "",
    intro_subtitle: "",
    sidebar_position: "right",
    logo_path: null,
    show_logo: true,
    show_licenses: true,
    show_credits: true,
    logo_position: "center",
    logo_sizing: "resize",
    logo_width: null,
    logo_height: null,
    scroll_background_color: null,
    scroll_title_color: null,
    scroll_section_title_color: null,
    scroll_name_color: null,    
    layout_style: "stacked",
    title_uppercase: false,
    name_uppercase: false,
    section_title_uppercase: true,
    swap_font_sizes_on_two_column: false,
    scroll_logo_path: null,
    scroll_logo_height: "120px",
  };

  // Tracks selected license for display
  let selected_license_name: string | null = null;

  // Toggles license content display
  function show_license(name: string) {
    selected_license_name = selected_license_name === name ? null : name;
  }

  // Reactive styles for dimensions and logo
  $: height_style =
    typeof height === "number" ? `${height}px` : height || "500px";
  $: width_style = typeof width === "number" ? `${width}px` : width || "100%";
  $: logo_width_style = effectiveValue.logo_width
    ? typeof effectiveValue.logo_width === "number"
      ? `${effectiveValue.logo_width}px`
      : effectiveValue.logo_width
    : "auto";
  $: logo_height_style = effectiveValue.logo_height
    ? typeof effectiveValue.logo_height === "number"
      ? `${effectiveValue.logo_height}px`
      : effectiveValue.logo_height
    : "100px";
  $: logo_panel_height = effectiveValue.logo_height
    ? typeof effectiveValue.logo_height === "number"
      ? `${effectiveValue.logo_height}px`
      : effectiveValue.logo_height
    : "100px";
  $: object_fit =
    effectiveValue.logo_sizing === "stretch"
      ? "fill"
      : effectiveValue.logo_sizing === "crop"
        ? "cover"
        : "contain";
  $: logo_justify =
    effectiveValue.logo_position === "center"
      ? "center"
      : effectiveValue.logo_position === "left"
        ? "flex-start"
        : "flex-end";
</script>

<Block
  {visible}
  {elem_id}
  {elem_classes}
  {container}
  {scale}
  {min_width}
  padding={false}
>
  <!-- Loading status tracker -->
  <StatusTracker
    autoscroll={gradio.autoscroll}
    i18n={gradio.i18n}
    queue_position={loading_status?.queue_position ?? -1}
    queue_size={loading_status?.queue_size ?? 0}
    status={loading_status?.status ?? "complete"}
  />
  <slot />

  <!-- Logo panel -->
  {#key effectiveValue.logo_position}
    <div class="outer-logo-wrapper" style:width={width_style}>
      {#if effectiveValue.show_logo && effectiveValue.logo_path?.url}
        <div
          class="logo-panel"
          style:height={logo_panel_height}
          style:display="flex"
          style:justify-content={logo_justify}
        >
          {#if gradio}
            <Image
              src={effectiveValue.logo_path.url}
              alt="Logo"
              loading="lazy"
              {gradio}
              style="width: {logo_width_style}; height: {logo_height_style}; object-fit: {object_fit};"
            />
          {:else}
            <img
              src={effectiveValue.logo_path.url}
              alt="Logo"
              style="width: {logo_width_style}; height: {logo_height_style}; object-fit: {object_fit};"
            />
          {/if}
        </div>
      {/if}
    </div>
  {/key}

  <!-- Credits and licenses panel -->
  {#if effectiveValue.show_licenses || effectiveValue.show_credits} 
    {#key effectiveValue.sidebar_position}
      <div class="outer-credits-wrapper" style:width={width_style}>
        <div
            class="credits-panel-wrapper"
            style:width={width_style}
            style:height={effectiveValue.sidebar_position === "right"
              ? height_style
              : undefined}
            style:--main-panel-width={!effectiveValue.show_credits && effectiveValue.show_licenses
              ? "0px"
              : "auto"}
          >
          {#if effectiveValue.show_credits}
            {#key { effect: effectiveValue.effect, speed: effectiveValue.speed }}
                <div
                  class="main-credits-panel"
                  style:height={height_style}
                  style:width={effectiveValue.sidebar_position === "right" &&
                  effectiveValue.show_licenses
                    ? "calc(100% - var(--sidebar-width, 400px))"
                    : width_style}
                >
                  {#if effectiveValue.effect === "scroll"}
                    <ScrollEffect
                      credits={effectiveValue.credits}
                      speed={effectiveValue.speed}
                      base_font_size={effectiveValue.base_font_size}
                      intro_title={effectiveValue.intro_title}
                      intro_subtitle={effectiveValue.intro_subtitle}
                      background_color={effectiveValue.scroll_background_color}
                      title_color={effectiveValue.scroll_title_color}
                      name_color={effectiveValue.scroll_name_color}                     
                      layout_style={effectiveValue.layout_style}
                      title_uppercase={effectiveValue.title_uppercase}
                      scroll_section_title_color={effectiveValue.scroll_section_title_color}
                      name_uppercase={effectiveValue.name_uppercase}
                      section_title_uppercase={effectiveValue.section_title_uppercase}
                      swap_font_sizes_on_two_column={effectiveValue.swap_font_sizes_on_two_column}
                      scroll_logo_path={effectiveValue.scroll_logo_path}
                      scroll_logo_height={effectiveValue.scroll_logo_height}
                    />
                  {:else if effectiveValue.effect === "starwars"}
                    <StarWarsEffect
                      credits={effectiveValue.credits}
                      speed={effectiveValue.speed}
                      base_font_size={effectiveValue.base_font_size}
                      intro_title={effectiveValue.intro_title}
                      intro_subtitle={effectiveValue.intro_subtitle}     
                      layout_style={effectiveValue.layout_style}
                      title_uppercase={effectiveValue.title_uppercase}
                      name_uppercase={effectiveValue.name_uppercase}
                      section_title_uppercase={effectiveValue.section_title_uppercase}
                      swap_font_sizes_on_two_column={effectiveValue.swap_font_sizes_on_two_column}           
                      scroll_logo_path={effectiveValue.scroll_logo_path}
                      scroll_logo_height={effectiveValue.scroll_logo_height}
                    />
                  {:else if effectiveValue.effect === "matrix"}
                    <MatrixEffect
                      credits={effectiveValue.credits}
                      speed={effectiveValue.speed}
                      base_font_size={effectiveValue.base_font_size}
                      intro_title={effectiveValue.intro_title}
                      intro_subtitle={effectiveValue.intro_subtitle}    
                      layout_style={effectiveValue.layout_style}
                      title_uppercase={effectiveValue.title_uppercase}
                      name_uppercase={effectiveValue.name_uppercase}
                      section_title_uppercase={effectiveValue.section_title_uppercase}
                      swap_font_sizes_on_two_column={effectiveValue.swap_font_sizes_on_two_column}            
                      scroll_logo_path={effectiveValue.scroll_logo_path}
                      scroll_logo_height={effectiveValue.scroll_logo_height}
                    />
                  {/if}
                </div>
            {/key}
          {/if}
          {#if effectiveValue.show_licenses && Object.keys(effectiveValue.licenses).length > 0}
            <div class="licenses-sidebar">
              <h3>Licenses</h3>
              <ul>
                {#each Object.entries(effectiveValue.licenses) as [name, content] (name)}
                  <li>
                    <button
                      class:selected={selected_license_name === name}
                      on:click={() => show_license(name)}
                      type="button"
                    >
                      {name}
                    </button>
                  </li>
                {/each}
              </ul>
              {#if selected_license_name}
                <div class="license-display">
                  <h4>{selected_license_name}</h4>
                  <pre>{effectiveValue.licenses[selected_license_name]}</pre>
                </div>
              {/if}
            </div>
          {/if}
        </div>
      </div>
    {/key}
  {/if}
</Block>

<svelte:head>
  {#if effectiveValue.sidebar_position === "bottom"}
    <!-- Bottom sidebar styles -->
    <style>
      .credits-panel-wrapper {
        flex-direction: column !important;
        --panel-direction: column;
        --sidebar-width: 100%;
        --border-left: none;
        --border-top: 1px solid var(--border-color-primary);
        --sidebar-max-height: 400px;
        --border: none;
      }
      .licenses-sidebar {
        width: 100% !important;
        border-left: none !important;
        border-top: 1px solid var(--border-color-primary) !important;
      }
      .main-credits-panel {
        width: 100% !important;
      }
    </style>
  {:else}
    <!-- Right sidebar styles -->
    <style>
            .credits-panel-wrapper { 
              flex-direction: row !important; 
              --panel-direction: row; 
              --sidebar-width: 400px; 
              --border-left: 1px solid var(--border-color-primary); 
              --border-top: none; 
              --border: none;
              --sidebar-max-height: {height_style}; 
            }
            .licenses-sidebar { width: var(--sidebar-width, 400px) !important; border-left: 1px solid var(--border-color-primary) !important; border-top: none !important; }
            .main-credits-panel { width: calc(100% - var(--sidebar-width, 400px)) !important; }
    </style>
  {/if}
</svelte:head>

<style>
  /* Remove default block styling */
  :global(.block) {
    border: none !important;
    box-shadow: none !important;
    border-style: none !important;
  }
  /* Logo wrapper */
  .outer-logo-wrapper {
    display: flex;
    flex-direction: column;
    width: 100%;
    border: none;
  }
  /* Credits wrapper */
  .outer-credits-wrapper {
    display: flex;
    flex-direction: column;
    width: 100%;
    border: none;
  }
  /* Logo panel */
  .logo-panel {
    background: var(--background-fill-primary);
    border: none;    
    display: flex !important;
    align-items: center;
    justify-content: var(--logo-justify, center);
    padding: 0px 0px 20px 0px;
    width: 100%;
  }
  /* Credits and licenses container */
  .credits-panel-wrapper {
    display: flex;
    flex-direction: var(--panel-direction, row);
    min-height: var(--size-full, 500px);
    width: 100%;
    background: var(--background-fill-primary);
    border: 1px solid var(--border-color-primary);
    border-radius: var(--radius-lg);
    overflow: hidden;
  }
  /* Credits display panel */
  .main-credits-panel {
    flex-grow: 1;
    flex-shrink: 1;
    min-width: 200px;
    background: black;
    overflow: hidden;
    position: relative;
  }
  /* Licenses sidebar */
  .licenses-sidebar {  
    width: calc(100% - var(--main-panel-width, 400px));
    max-width: 100%;
    max-height: var(--sidebar-max-height, none);
    flex-shrink: 1;
    flex-grow: 1; 
    background: var(--background-fill-secondary);
    overflow-y: auto;
    border-left: var(--border-left, 1px solid var(--border-color-primary));
    border-top: var(--border-top, none);
}
  .licenses-sidebar h3 {
    margin: var(--spacing-lg);
    font-size: var(--text-lg);
  }
  .licenses-sidebar li {
    padding: 0;
    margin: 0;
    cursor: default;
    border-bottom: 1px solid var(--border-color-primary);
  }
  .licenses-sidebar li button {
    background: none;
    border: none;
    font: inherit;
    color: inherit;
    text-align: left;
    width: 100%;
    cursor: pointer;
    padding: var(--spacing-md) var(--spacing-lg);
    transition: background-color 0.2s;
  }
  .licenses-sidebar li button:hover {
    background-color: var(--background-fill-primary);
  }
  .licenses-sidebar li button:focus-visible {
    outline: 2px solid var(--color-accent);
    outline-offset: -2px;
  }
  .licenses-sidebar li button.selected {
    background-color: var(--color-accent);
    color: white;
    font-weight: bold;
  }
  .license-display {
    padding: var(--spacing-lg);
    overflow-y: auto;
    flex-grow: 1;
    border-top: 1px solid var(--border-color-primary);
    background: var(--background-fill-primary);
  }
  .license-display h4 {
    margin-top: 0;
  }
  .license-display pre {
    white-space: pre-wrap;
    word-break: break-word;
    font-size: var(--text-sm);
    color: var(--body-text-color-subdued);
  }
</style>
