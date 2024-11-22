<script lang="ts">
    
</script>

<style>
    #toolTip {
        position: absolute;
        background: white;
        border: 1px solid rgba(0, 0, 0, 0.2);
        padding: 12px;
        border-radius: 8px;
        pointer-events: none;
        transform: translate(-50%, -100%);
        display: none;
        white-space: nowrap;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
        font-family: Arial, sans-serif;
        font-size: 10px;
        line-height: 1.5;
        text-align: left;
        z-index: 10;
    }
    #toolTip::after {
        content: "";
        position: absolute;
        bottom: -5px;
        left: 50%;
        transform: translateX(-50%);
        border-width: 5px;
        border-style: solid;
        border-color: white transparent transparent transparent;
    }
</style>

<div id="toolTip"></div>