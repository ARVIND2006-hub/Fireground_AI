#include <stdint.h>
#include "traffic_regs.h"

/*
 * Example firmware skeleton for a soft processor with memory-mapped access.
 * Replace TRAFFIC_MMIO_BASE with the address assigned in the actual platform.
 * This file is a reference example; it is not a complete board-specific app.
 */
#ifndef TRAFFIC_MMIO_BASE
#define TRAFFIC_MMIO_BASE ((uintptr_t)0x40000000u)
#endif

static volatile void *const traffic = (volatile void *)TRAFFIC_MMIO_BASE;

int main(void)
{
    /* Keep sensor status valid and start with all request levels cleared. */
    traffic_set_control(traffic, TRAFFIC_CONTROL_SENSOR_VALID);

    /* Example: North/South demand 5, East/West demand 9. */
    traffic_set_demand(traffic, 5u, 9u);

    for (;;) {
        uint32_t status = traffic_get_status(traffic);
        uint32_t debug = traffic_get_debug(traffic);

        /*
         * Connect status/debug to a UART, display, or telemetry task here.
         * Avoid busy-loop assumptions about real-time timing; use platform
         * interrupts or a scheduler in a real embedded application.
         */
        (void)status;
        (void)debug;
    }
}
