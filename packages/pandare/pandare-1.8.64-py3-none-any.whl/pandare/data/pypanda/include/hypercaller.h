
typedef void (*hypercall_t)(CPUState *cpu);
void register_hypercall(uint32_t magic, hypercall_t);
void unregister_hypercall(uint32_t magic);

