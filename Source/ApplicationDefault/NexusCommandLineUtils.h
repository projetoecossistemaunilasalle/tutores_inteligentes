#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "NexusCommandLineUtils.generated.h"

/**
 * Utilit?ios de linha de comando para o NexusBite_Hub.
 */
UCLASS()
class APPLICATIONDEFAULT_API UNexusCommandLineUtils : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/**
	 * Retorna a string de inicializa?o EXATAMENTE como foi enviada pelo OS.
	 * N? cont? filtros, n? remove o caminho do execut?el e n? faz parse.
	 */
	UFUNCTION(BlueprintPure, Category = "Nexus|System")
	static FString GetNexusRawCommandLine();
};