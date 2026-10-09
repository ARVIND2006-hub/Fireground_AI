#ifndef TRAFFIC_REGS_H
#define TRAFFIC_REGS_H

#include <stdint.h>

/* Byte offsets from the peripheral base address assigned by the SoC integrator. */
#define TRAFFIC_REG_CONTROL 0x00u
#define TRAFFIC_REG_DEMAND  0x04u
#define TRAFFIC_REG_STATUS  0x08u
#define TRAFFIC_REG_DEBUG   0x0Cu

#define TRAFFIC_CONTROL_SENSOR_VALID (1u << 0)
#define TRAFFIC_CONTROL_NS_EMERGENCY (1u << 1)
#define TRAFFIC_CONTROL_EW_EMERGENCY (1u << 2)
#define TRAFFIC_CONTROL_PED_NS       (1u << 3)
#define TRAFFIC_CONTROL_PED_EW       (1u << 4)

#define TRAFFIC_DEMAND_NS(value) ((uint32_t)(value) & 0x0Fu)
#define TRAFFIC_DEMAND_EW(value) (((uint32_t)(value) & 0x0Fu) << 4)

#define TRAFFIC_STATUS_NS_LIGHT_MASK 0x00000003u
#define TRAFFIC_STATUS_EW_LIGHT_MASK 0x0000000Cu
#define TRAFFIC_STATUS_PED_NS        (1u << 4)
#define TRAFFIC_STATUS_PED_EW        (1u << 5)
#define TRAFFIC_STATUS_EMERGENCY     (1u << 6)
#define TRAFFIC_STATUS_FAULT         (1u << 7)

#define TRAFFIC_DEBUG_STATE_MASK     0x0000000Fu
#define TRAFFIC_DEBUG_TIMER_SHIFT    4u

/*
 * Use only when the platform maps this peripheral into the CPU address space.
 * The base address is deliberately supplied by the platform, never hard-coded.
 */
static inline volatile uint32_t *traffic_reg(volatile void *base, uint32_t offset)
{
    return (volatile uint32_t *)((volatile uint8_t *)base + offset);
}

static inline void traffic_set_demand(volatile void *base,
                                      uint8_t ns, uint8_t ew)
{
    *traffic_reg(base, TRAFFIC_REG_DEMAND) =
        TRAFFIC_DEMAND_NS(ns) | TRAFFIC_DEMAND_EW(ew);
}

static inline void traffic_set_control(volatile void *base, uint32_t control)
{
    *traffic_reg(base, TRAFFIC_REG_CONTROL) = control & 0x1Fu;
}

static inline uint32_t traffic_get_status(volatile void *base)
{
    return *traffic_reg(base, TRAFFIC_REG_STATUS);
}

static inline uint32_t traffic_get_debug(volatile void *base)
{
    return *traffic_reg(base, TRAFFIC_REG_DEBUG);
}

#endif
