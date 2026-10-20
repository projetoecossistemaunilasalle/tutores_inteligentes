#include "NexusSubsystemBasic.h"

void UNexusSubsystemBasic::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	// Chama o evento implementado no Blueprint
	OnSubsystemInitialize();
}

void UNexusSubsystemBasic::Deinitialize()
{
	// Chama o evento de limpeza no Blueprint
	OnSubsystemDeinitialize();
	Super::Deinitialize();
}