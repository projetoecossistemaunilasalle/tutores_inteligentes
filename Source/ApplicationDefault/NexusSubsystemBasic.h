#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
// O include .generated.h deve ser sempre o ?timo
#include "NexusSubsystemBasic.generated.h"

/**
 * UNexusSubsystemBasic: Classe base corrigida para o m?ulo ApplicationDefault.
 */
UCLASS(Abstract, Blueprintable, BlueprintType)
class APPLICATIONDEFAULT_API UNexusSubsystemBasic : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	// Evento para inicializa?o no Blueprint
	UFUNCTION(BlueprintImplementableEvent, Category = "NexusEngine")
	void OnSubsystemInitialize();

	// Evento para encerramento no Blueprint
	UFUNCTION(BlueprintImplementableEvent, Category = "NexusEngine")
	void OnSubsystemDeinitialize();

	// Fun?es nativas da Engine
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;
};